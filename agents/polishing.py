from __future__ import annotations

from typing import Any, Optional

from message_polishing.context import append_event, build_polishing_payload, model_to_payload
from message_polishing.llm import LLMClientProtocol
from message_polishing.prompts import POLISHING_SYSTEM_PROMPT
from message_polishing.schemas import (
    FeatureAnalysisResult,
    MessagePolishingState,
    PolishingResult,
    PolishingValidationResult,
    coerce_model,
)


REQUIRED_VALIDATION_CHECKS = [
    "preserves_user_intent",
    "no_hallucinated_facts",
    "appropriate_relationship_tone",
    "clear_request_or_message",
    "concise_enough",
    "grammar_naturalness",
    "follows_extra_requests",
    "follows_revision_instruction",
]

CRITICAL_VALIDATION_CHECKS = {
    "preserves_user_intent",
    "no_hallucinated_facts",
    "follows_revision_instruction",
    "appropriate_relationship_tone",
    "clear_request_or_message",
}

CRITICAL_ISSUE_PHRASES = [
    "원문 의도 변경",
    "의도 변경",
    "hallucinated",
    "hallucination",
    "사용자가 말하지 않은",
    "구체 사실 추가",
    "revision_instruction 미반영",
    "지시 미반영",
    "관계에 심각하게 맞지",
    "말투",
    "불명확",
    "이해하기 어려운",
]


_SPECIFIC_FACT_TOKENS = [
    "병원",
    "가족",
    "회의",
    "출장",
    "면접",
    "사고",
    "수술",
    "감기",
    "급한",
    "가능한 한 빨리",
    "오늘",
    "내일",
    "모레",
    "이번 주",
    "다음 주",
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일",
]


def _text_from_context(context: Optional[dict[str, Any] | str]) -> str:
    if context is None:
        return ""
    return str(context)


def _analysis_allowed_text(analysis: Optional[FeatureAnalysisResult]) -> str:
    if not analysis:
        return ""
    return " ".join([*analysis.constraints, *analysis.extra_requests])


def _allowed_source_text(
    state: MessagePolishingState,
    analysis: Optional[FeatureAnalysisResult] = None,
) -> str:
    return " ".join(
        str(value)
        for value in [
            state.get("original_message"),
            state.get("user_feedback_message"),
            _text_from_context(state.get("user_context")),
            state.get("context_summary"),
            _analysis_allowed_text(analysis),
        ]
        if value
    )


def _contains_hallucinated_specific_facts(message: str, source_text: str) -> bool:
    return any(token in message and token not in source_text for token in _SPECIFIC_FACT_TOKENS)


def _has_critical_issue(issues: list[str]) -> bool:
    for issue in issues:
        issue_text = str(issue)
        if issue_text in CRITICAL_VALIDATION_CHECKS:
            return True
        if any(phrase in issue_text for phrase in CRITICAL_ISSUE_PHRASES):
            return True
    return False


def _has_formal_tone(message: str) -> bool:
    return any(marker in message for marker in ["님", "습니다", "드립니다", "여쭙", "부탁드립니다"])


def _is_clear_request(message: str) -> bool:
    return any(marker in message for marker in ["가능", "부탁", "요청", "여쭙", "괜찮", "문의"])


def _contains_apology(message: str) -> bool:
    return any(marker in message for marker in ["죄송", "송구", "사과", "양해"])


def _reflects_instruction_text(message: str, instruction: str) -> bool:
    if not instruction:
        return True
    if "금요일" in instruction and "금요일" not in message:
        return False
    if any(keyword in instruction for keyword in ["죄송", "사과", "송구"]) and not _contains_apology(message):
        return False
    if any(keyword in instruction for keyword in ["짧", "간결"]) and len(message) > 220:
        return False
    if any(keyword in instruction for keyword in ["정중", "공손"]) and not _has_formal_tone(message):
        return False
    return True


def validate_polished_message(
    *,
    state: MessagePolishingState,
    polished_message: str,
    analysis: Optional[FeatureAnalysisResult],
) -> PolishingValidationResult:
    source_text = _allowed_source_text(state, analysis)
    feedback = state.get("user_feedback_message") or ""
    revision_instruction = state.get("revision_instruction") or ""
    relationship_text = " ".join(
        value for value in [analysis.relationship if analysis else None, analysis.recipient if analysis else None] if value
    )
    extra_request_text = " ".join(analysis.extra_requests if analysis else [])

    checks = {
        "preserves_user_intent": bool(polished_message.strip()),
        "no_hallucinated_facts": not _contains_hallucinated_specific_facts(polished_message, source_text),
        "appropriate_relationship_tone": True,
        "clear_request_or_message": bool(polished_message.strip()),
        "concise_enough": len(polished_message) <= 600,
        "grammar_naturalness": "  " not in polished_message and polished_message.strip() == polished_message,
        "follows_extra_requests": True,
        "follows_revision_instruction": True,
    }

    if any(keyword in relationship_text for keyword in ["교수", "상사", "팀장", "부장", "고객", "선생"]):
        checks["appropriate_relationship_tone"] = _has_formal_tone(polished_message)

    if any(keyword in source_text for keyword in ["요청", "가능", "될까요", "해도", "연장", "문의"]):
        checks["clear_request_or_message"] = _is_clear_request(polished_message)

    if any(keyword in feedback for keyword in ["죄송", "미안", "송구", "사과"]):
        checks["follows_extra_requests"] = checks["follows_extra_requests"] and _contains_apology(polished_message)
    if "금요일" in feedback:
        checks["follows_extra_requests"] = checks["follows_extra_requests"] and "금요일" in polished_message
    if any(keyword in feedback for keyword in ["짧", "간결"]):
        checks["follows_extra_requests"] = checks["follows_extra_requests"] and len(polished_message) <= 220

    if "사과 표현 강화" in extra_request_text:
        checks["follows_extra_requests"] = checks["follows_extra_requests"] and _contains_apology(polished_message)
    if "금요일" in extra_request_text:
        checks["follows_extra_requests"] = checks["follows_extra_requests"] and "금요일" in polished_message
    if "짧고 간결" in extra_request_text:
        checks["follows_extra_requests"] = checks["follows_extra_requests"] and len(polished_message) <= 220
    if "정중" in extra_request_text or "공손" in extra_request_text:
        checks["follows_extra_requests"] = checks["follows_extra_requests"] and _has_formal_tone(polished_message)

    checks["follows_revision_instruction"] = _reflects_instruction_text(
        polished_message,
        revision_instruction,
    )

    issues = [check for check, passed in checks.items() if not passed]
    score = sum(1 for passed in checks.values() if passed) / len(checks)
    critical_failed = _has_critical_issue(issues)
    return PolishingValidationResult(
        passed=score >= 0.75
        and not critical_failed
        and checks["preserves_user_intent"]
        and checks["no_hallucinated_facts"]
        and checks["grammar_naturalness"],
        score=score,
        issues=issues,
        checks=checks,
    )


def merge_validation_results(
    llm_validation: PolishingValidationResult,
    deterministic_validation: PolishingValidationResult,
) -> PolishingValidationResult:
    checks = {check: bool(llm_validation.checks.get(check, True)) for check in REQUIRED_VALIDATION_CHECKS}
    checks.update({check: bool(value) for check, value in deterministic_validation.checks.items()})
    for check in REQUIRED_VALIDATION_CHECKS:
        checks[check] = bool(llm_validation.checks.get(check, True)) and bool(
            deterministic_validation.checks.get(check, True)
        )
    issues = list(dict.fromkeys([*llm_validation.issues, *deterministic_validation.issues]))
    score = min(llm_validation.score, deterministic_validation.score)
    critical_failed = _has_critical_issue(issues)
    return PolishingValidationResult(
        passed=score >= 0.75
        and not critical_failed
        and checks.get("preserves_user_intent", False)
        and checks.get("no_hallucinated_facts", False)
        and checks.get("grammar_naturalness", False),
        score=score,
        issues=issues,
        checks=checks,
    )


def _needs_self_revision(validation: PolishingValidationResult) -> bool:
    return validation.score < 0.75 or _has_critical_issue(validation.issues)


def _sanitize_hallucinated_specific_facts(message: str, source_text: str) -> str:
    sanitized = message
    if "급한" not in source_text:
        replacements = {
            "급한 일이 생겨서": "개인적인 사정으로",
            "급한 일이 생겨": "개인적인 사정으로",
            "급한 일이 발생해": "개인적인 사정으로",
            "급한 일이 있어": "개인적인 사정이 있어",
            "급한 일로": "개인적인 사정으로",
            "급하게": "",
        }
        for old, new in replacements.items():
            sanitized = sanitized.replace(old, new)

    if "병원" not in source_text:
        sanitized = sanitized.replace("병원 일정으로 인해", "개인적인 사정으로")
        sanitized = sanitized.replace("병원 일정 때문에", "개인적인 사정으로")

    unsupported_meta_phrases = [
        "구체적인 희망 기한을 아직 정하지 못해 죄송합니다.",
        "구체적인 희망 기한을 알려주시면 감사하겠습니다.",
        "희망 기한을 알려주시면 감사하겠습니다.",
        "구체적인 기한을 알려주시면 감사하겠습니다.",
        "가능한 한 빨리 알려드리겠습니다.",
    ]
    for phrase in unsupported_meta_phrases:
        sanitized = sanitized.replace(phrase, "")

    if "희망 기한" not in source_text:
        sanitized = _remove_sentences_containing(sanitized, ["희망 기한", "구체적인 기한"])

    if "가능한 한 빨리" not in source_text:
        sanitized = _remove_sentences_containing(sanitized, ["가능한 한 빨리"])

    if any(keyword in source_text for keyword in ["죄송", "미안", "덜 죄송", "사과"]) and "죄송" not in sanitized:
        sanitized = f"{sanitized.rstrip()} 죄송합니다."

    while "  " in sanitized:
        sanitized = sanitized.replace("  ", " ")
    return sanitized.strip()


def _remove_sentences_containing(message: str, blocked_terms: list[str]) -> str:
    sentences = [sentence.strip() for sentence in message.split(".")]
    kept: list[str] = []
    for sentence in sentences:
        if not sentence:
            continue
        if any(term in sentence for term in blocked_terms):
            continue
        kept.append(sentence)
    if not kept:
        return ""
    joined = ". ".join(kept)
    return joined if joined[-1] in ".?!" else f"{joined}."


class PolishingAgent:
    def __init__(self, llm_client: LLMClientProtocol) -> None:
        self.llm_client = llm_client

    def __call__(self, state: MessagePolishingState) -> MessagePolishingState:
        analysis = coerce_model(state.get("analysis"), FeatureAnalysisResult)
        payload = build_polishing_payload(state)
        result = self.llm_client.generate_json(
            system_prompt=POLISHING_SYSTEM_PROMPT,
            user_payload=payload,
            response_schema=PolishingResult,
            attachments=state.get("attachments"),
        )
        result = self._with_deterministic_validation(state, result, analysis)

        if _needs_self_revision(result.validation):
            result = self._self_revise_once(state, result, analysis)

        if not result.validation.checks.get("no_hallucinated_facts", True):
            result = self._sanitize_once(state, result, analysis)

        consumed_revision = bool(state.get("revision_instruction"))
        next_iteration = int(state.get("feedback_iteration", 0)) + 1 if consumed_revision else int(
            state.get("feedback_iteration", 0)
        )

        return {
            "current_polished_message": result.polished_message,
            "polishing_validation": result.validation,
            "revision_instruction": None,
            "feedback_iteration": next_iteration,
            "events": append_event(
                state,
                node="polishing",
                message="Polishing completed.",
                details={
                    "validation": model_to_payload(result.validation),
                    "revision_notes": result.revision_notes,
                    "consumed_revision_instruction": consumed_revision,
                },
            ),
        }

    def _with_deterministic_validation(
        self,
        state: MessagePolishingState,
        result: PolishingResult,
        analysis: Optional[FeatureAnalysisResult],
    ) -> PolishingResult:
        deterministic_validation = validate_polished_message(
            state=state,
            polished_message=result.polished_message,
            analysis=analysis,
        )
        validation = merge_validation_results(result.validation, deterministic_validation)
        return result.model_copy(update={"validation": validation})

    def _self_revise_once(
        self,
        state: MessagePolishingState,
        result: PolishingResult,
        analysis: Optional[FeatureAnalysisResult],
    ) -> PolishingResult:
        revision_instruction = (
            "Polishing validation failed. Rewrite once while preserving the original intent, "
            "removing hallucinated details, and fixing these issues: "
            f"{', '.join(result.validation.issues)}"
        )
        payload = build_polishing_payload(
            {
                **state,
                "current_polished_message": result.polished_message,
                "revision_instruction": revision_instruction,
            }
        )
        revised = self.llm_client.generate_json(
            system_prompt=POLISHING_SYSTEM_PROMPT,
            user_payload=payload,
            response_schema=PolishingResult,
            attachments=state.get("attachments"),
        )
        revised = self._with_deterministic_validation(
            {**state, "revision_instruction": revision_instruction},
            revised,
            analysis,
        )
        revision_notes = list(dict.fromkeys([*result.revision_notes, *revised.revision_notes, revision_instruction]))
        return revised.model_copy(update={"revision_notes": revision_notes})

    def _sanitize_once(
        self,
        state: MessagePolishingState,
        result: PolishingResult,
        analysis: Optional[FeatureAnalysisResult],
    ) -> PolishingResult:
        sanitized_message = _sanitize_hallucinated_specific_facts(
            result.polished_message,
            _allowed_source_text(state, analysis),
        )
        validation = validate_polished_message(
            state=state,
            polished_message=sanitized_message,
            analysis=analysis,
        )
        revision_notes = list(
            dict.fromkeys(
                [
                    *result.revision_notes,
                    "Removed or generalized unsupported specific facts after self-revision.",
                ]
            )
        )
        return result.model_copy(
            update={
                "polished_message": sanitized_message,
                "validation": validation,
                "revision_notes": revision_notes,
            }
        )
