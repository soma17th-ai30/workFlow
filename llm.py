from __future__ import annotations

import json
from typing import Any, Optional, Protocol, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from message_polishing.schemas import AttachmentInput
from message_polishing.settings import MessagePolishingSettings


T = TypeVar("T", bound=BaseModel)


class LLMClientProtocol(Protocol):
    def generate_json(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        response_schema: type[T],
        attachments: Optional[list[AttachmentInput]] = None,
    ) -> T:
        ...


class LLMError(RuntimeError):
    pass


class LLMTimeoutError(LLMError):
    pass


class LLMResponseError(LLMError):
    pass


class LLMValidationError(LLMError):
    pass


class UpstageResponsesClient:
    def __init__(
        self,
        settings: Optional[MessagePolishingSettings] = None,
        *,
        client: Optional[OpenAI] = None,
    ) -> None:
        self.settings = settings or MessagePolishingSettings.from_env()
        self.client = client or OpenAI(
            api_key=self.settings.require_api_key(),
            base_url=self.settings.chat_base_url,
            timeout=self.settings.timeout_seconds,
        )

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        response_schema: type[T],
        attachments: Optional[list[AttachmentInput]] = None,
    ) -> T:
        input_payload = self._build_input_payload(
            system_prompt=system_prompt,
            user_payload=user_payload,
            response_schema=response_schema,
            attachments=attachments,
        )
        raw_output = self._create_chat_completion(input_payload)
        try:
            return self._parse_json_response(raw_output, response_schema)
        except (json.JSONDecodeError, ValidationError) as exc:
            repaired_output = self._repair_json(
                system_prompt=system_prompt,
                original_payload=user_payload,
                raw_output=raw_output,
                error=str(exc),
                response_schema=response_schema,
            )
            try:
                return self._parse_json_response(repaired_output, response_schema)
            except (json.JSONDecodeError, ValidationError) as repair_exc:
                raise LLMValidationError(
                    f"LLM response did not match {response_schema.__name__} after one repair attempt: {repair_exc}"
                ) from repair_exc

    def _build_input_payload(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        response_schema: type[BaseModel],
        attachments: Optional[list[AttachmentInput]],
    ) -> list[dict[str, Any]]:
        schema_payload = response_schema.model_json_schema()
        user_text = json.dumps(
            {
                "system_instructions": system_prompt,
                "task_payload": user_payload,
                "response_schema": schema_payload,
                "output_contract": "Return exactly one JSON object matching response_schema. Do not include markdown or code fences.",
            },
            ensure_ascii=False,
            default=str,
        )

        user_content: list[dict[str, Any]] = [{"type": "input_text", "text": user_text}]
        for attachment in attachments or []:
            file_id = self._resolve_file_id(attachment)
            if file_id:
                user_content.append({"type": "input_file", "file_id": file_id})

        return [{"role": "user", "content": user_content}]

    def _resolve_file_id(self, attachment: AttachmentInput) -> Optional[str]:
        if attachment.fileId:
            return attachment.fileId
        if not attachment.path:
            return None

        with open(attachment.path, "rb") as file_obj:
            uploaded = self.client.files.create(file=file_obj, purpose="user_data")
        return uploaded.id

    def _create_chat_completion(self, input_payload: list[dict[str, Any]]) -> str:
        if self._has_input_files(input_payload):
            raise LLMError(
                "File attachments require a Studio Agent/Responses API flow. "
                "solar-pro3 chat mode supports text input."
            )

        create_kwargs: dict[str, Any] = {
            "model": self.settings.model,
            "messages": [{"role": "user", "content": self._extract_text_content(input_payload)}],
        }
        if self.settings.temperature is not None:
            create_kwargs["temperature"] = self.settings.temperature

        response = self.client.chat.completions.create(**create_kwargs)
        output_text = response.choices[0].message.content if response.choices else None
        if not output_text:
            raise LLMResponseError("Chat completion did not include message content.")
        return output_text

    def _has_input_files(self, input_payload: list[dict[str, Any]]) -> bool:
        for message in input_payload:
            for content_item in message.get("content", []):
                if content_item.get("type") == "input_file":
                    return True
        return False

    def _extract_text_content(self, input_payload: list[dict[str, Any]]) -> str:
        texts: list[str] = []
        for message in input_payload:
            for content_item in message.get("content", []):
                if content_item.get("type") == "input_text":
                    texts.append(content_item.get("text", ""))
        return "\n\n".join(text for text in texts if text)

    def _parse_json_response(self, raw_output: str, response_schema: type[T]) -> T:
        parsed = self._load_json_object(raw_output)
        return response_schema.model_validate(parsed)

    def _load_json_object(self, raw_output: str) -> Any:
        stripped = raw_output.strip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            parsed, _ = json.JSONDecoder().raw_decode(stripped)
            return parsed

    def _repair_json(
        self,
        *,
        system_prompt: str,
        original_payload: dict[str, Any],
        raw_output: str,
        error: str,
        response_schema: type[BaseModel],
    ) -> str:
        repair_system_prompt = (
            f"{system_prompt}\n\n"
            "이전 응답이 JSON parsing 또는 schema validation에 실패했다. "
            "원래 task_payload의 의미를 유지하면서 response_schema에 맞는 JSON object 하나만 다시 출력하라."
        )
        repair_payload = {
            "original_task_payload": original_payload,
            "invalid_model_output": raw_output,
            "validation_error": error,
            "response_schema": response_schema.model_json_schema(),
        }
        repair_input_payload = self._build_input_payload(
            system_prompt=repair_system_prompt,
            user_payload=repair_payload,
            response_schema=response_schema,
            attachments=None,
        )
        return self._create_chat_completion(repair_input_payload)
