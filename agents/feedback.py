from __future__ import annotations

from message_polishing.context import append_event, build_feedback_payload, model_to_payload
from message_polishing.llm import LLMClientProtocol
from message_polishing.prompts import FEEDBACK_SYSTEM_PROMPT
from message_polishing.schemas import FeedbackResult, MessagePolishingState


def split_feedback_items(feedback_message: str | None) -> list[str]:
    if not feedback_message:
        return []
    items: list[str] = []
    if any(keyword in feedback_message for keyword in ["죄송", "미안", "송구", "사과"]):
        items.append("사과 표현 강화")
    if "금요일" in feedback_message:
        items.append("금요일까지 제출 가능 내용 포함")
    if any(keyword in feedback_message for keyword in ["짧", "간결"]):
        items.append("더 짧고 간결하게 작성")
    if any(keyword in feedback_message for keyword in ["정중", "공손"]):
        items.append("더 정중하게 작성")
    if any(keyword in feedback_message for keyword in ["자연", "딱딱"]):
        items.append("더 자연스럽게 작성")
    if any(keyword in feedback_message for keyword in ["부드럽", "완곡"]):
        items.append("더 부드럽게 작성")
    if not items:
        items.append(feedback_message.strip())
    return list(dict.fromkeys(items))


def _item_is_reflected(item: str, polished_message: str) -> bool:
    if item == "사과 표현 강화":
        return any(marker in polished_message for marker in ["죄송", "송구", "사과", "양해"])
    if item == "금요일까지 제출 가능 내용 포함":
        return "금요일" in polished_message
    if item == "더 짧고 간결하게 작성":
        return len(polished_message) <= 220
    if item == "더 정중하게 작성":
        return any(marker in polished_message for marker in ["습니다", "드립니다", "여쭙", "부탁드립니다"])
    if item == "더 자연스럽게 작성":
        return "귀하" not in polished_message and "상기" not in polished_message
    if item == "더 부드럽게 작성":
        return any(marker in polished_message for marker in ["혹시", "가능하시다면", "괜찮으실지", "양해"])
    return True


def reconcile_feedback_result(
    result: FeedbackResult,
    *,
    feedback_items: list[str],
    polished_message: str,
) -> FeedbackResult:
    unresolved = [item for item in feedback_items if not _item_is_reflected(item, polished_message)]
    applied = [item for item in feedback_items if item not in unresolved]
    checks = dict(result.checks)
    checks["reflects_user_feedback"] = not unresolved
    if unresolved:
        instruction = (
            "사용자 피드백 중 아직 반영되지 않은 항목을 반영해서 다시 작성하라: "
            f"{', '.join(unresolved)}. "
            "원문의 의도와 이전 초안의 유효한 내용은 유지하고, 사용자가 말하지 않은 구체 사실은 추가하지 말라."
        )
        issues = list(dict.fromkeys([*result.issues, "unresolved_user_feedback"]))
        return result.model_copy(
            update={
                "feedback_satisfied": False,
                "revision_needed": True,
                "revision_instruction": result.revision_instruction or instruction,
                "unresolved_feedback_items": unresolved,
                "applied_feedback_items": applied,
                "score": min(result.score, 0.74),
                "issues": issues,
                "checks": checks,
            }
        )

    return result.model_copy(
        update={
            "feedback_satisfied": True,
            "revision_needed": False,
            "revision_instruction": None,
            "unresolved_feedback_items": [],
            "applied_feedback_items": applied or result.applied_feedback_items,
            "score": max(result.score, 0.9),
            "checks": checks,
        }
    )


class FeedbackAgent:
    def __init__(self, llm_client: LLMClientProtocol) -> None:
        self.llm_client = llm_client

    def __call__(self, state: MessagePolishingState) -> MessagePolishingState:
        feedback_message = state.get("user_feedback_message")
        if not feedback_message:
            result = FeedbackResult(
                feedback_satisfied=True,
                revision_needed=False,
                revision_instruction=None,
                unresolved_feedback_items=[],
                applied_feedback_items=[],
                score=1.0,
                issues=[],
                checks={
                    "reflects_user_feedback": True,
                    "preserves_original_intent": True,
                    "preserves_valid_existing_content": True,
                    "no_new_hallucinated_facts": True,
                    "tone_adjusted_correctly": True,
                    "concise_enough": True,
                },
            )
        else:
            feedback_items = split_feedback_items(feedback_message)
            payload = build_feedback_payload(state, feedback_items)
            result = self.llm_client.generate_json(
                system_prompt=FEEDBACK_SYSTEM_PROMPT,
                user_payload=payload,
                response_schema=FeedbackResult,
                attachments=state.get("attachments"),
            )
            result = reconcile_feedback_result(
                result,
                feedback_items=feedback_items,
                polished_message=state.get("current_polished_message") or "",
            )

        return {
            "feedback_result": result,
            "revision_instruction": result.revision_instruction if result.revision_needed else None,
            "events": append_event(
                state,
                node="feedback",
                message="Feedback evaluation completed.",
                details=model_to_payload(result),
            ),
        }
