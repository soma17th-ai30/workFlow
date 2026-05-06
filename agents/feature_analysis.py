from __future__ import annotations

from typing import Any, Optional

from message_polishing.context import append_event, build_feature_analysis_payload
from message_polishing.llm import LLMClientProtocol
from message_polishing.prompts import FEATURE_ANALYSIS_SYSTEM_PROMPT
from message_polishing.schemas import FeatureAnalysisResult, MessagePolishingState


def _combined_text(*values: Any) -> str:
    return " ".join(str(value) for value in values if value)


def analyze_intent(
    original_message: str,
    user_feedback_message: Optional[str] = None,
    user_context: Optional[dict[str, Any] | str] = None,
) -> Optional[str]:
    text = _combined_text(original_message, user_feedback_message, user_context)
    if "과제" in text and ("제출" in text or "기한" in text) and ("늦" in text or "연장" in text):
        return "과제 제출 기한 연장 요청"
    if "일정" in text or "시간" in text or "약속" in text:
        return "일정 조율"
    if "감사" in text or "고맙" in text:
        return "감사 표현"
    if "죄송" in text or "사과" in text:
        return "사과"
    if "거절" in text or "어렵" in text:
        return "거절 또는 양해 요청"
    if "확인" in text or "문의" in text:
        return "확인 요청"
    return None


def analyze_relationship(
    original_message: str,
    user_context: Optional[dict[str, Any] | str] = None,
) -> tuple[Optional[str], Optional[str]]:
    text = _combined_text(original_message, user_context)
    if "교수님" in text:
        return "학생 -> 교수", "교수님"
    if "선생님" in text:
        return "학생 또는 보호자 -> 선생님", "선생님"
    if "팀장님" in text:
        return "직원 -> 팀장", "팀장님"
    if "부장님" in text:
        return "직원 -> 부장", "부장님"
    if "상사" in text:
        return "직원 -> 상사", None
    if "고객" in text or "고객님" in text:
        return "고객 또는 업체 관계", "고객님" if "고객님" in text else None
    if "동료" in text:
        return "동료 간", None
    return None, None


def analyze_tone(
    original_message: str,
    user_feedback_message: Optional[str] = None,
    relationship: Optional[str] = None,
) -> Optional[str]:
    text = _combined_text(original_message, user_feedback_message, relationship)
    tones: list[str] = []
    if any(keyword in text for keyword in ["교수", "상사", "팀장", "부장", "고객", "정중"]):
        tones.append("정중함")
    if any(keyword in text for keyword in ["죄송", "사과", "미안", "송구"]):
        tones.append("사과 중심")
    if "짧" in text or "간결" in text:
        tones.append("간결함")
    if "자연" in text or "딱딱" in text:
        tones.append("자연스러움")
    if "친근" in text or "편하게" in text:
        tones.append("친근함")
    if not tones:
        return None
    return ", ".join(dict.fromkeys(tones))


def analyze_extra_requests(user_feedback_message: Optional[str], original_message: str = "") -> list[str]:
    text = _combined_text(user_feedback_message, original_message)
    requests: list[str] = []
    if not text:
        return requests
    if any(keyword in text for keyword in ["죄송", "미안", "송구", "사과"]):
        requests.append("사과 표현 강화")
    if "금요일" in text:
        requests.append("금요일까지 제출 가능하다는 내용 포함")
    if any(keyword in text for keyword in ["짧", "간결"]):
        requests.append("더 짧고 간결하게 작성")
    if any(keyword in text for keyword in ["정중", "공손"]):
        requests.append("더 정중하게 작성")
    if any(keyword in text for keyword in ["자연", "딱딱"]):
        requests.append("더 자연스럽게 작성")
    if any(keyword in text for keyword in ["부드럽", "완곡"]):
        requests.append("더 부드럽게 작성")
    return list(dict.fromkeys(requests))


def analyze_missing_info(
    original_message: str,
    user_feedback_message: Optional[str] = None,
) -> list[str]:
    text = _combined_text(original_message, user_feedback_message)
    missing: list[str] = []
    if ("늦" in text or "연장" in text) and not any(
        keyword in text for keyword in ["오늘", "내일", "이번 주", "금요일", "월요일", "화요일", "수요일", "목요일", "토요일", "일요일"]
    ):
        missing.append("구체적인 희망 기한")
    if "일이 있어서" in original_message or "사정" in original_message:
        missing.append("구체적인 사유")
    return missing


def _communication_channel(original_message: str, user_context: Optional[dict[str, Any] | str]) -> Optional[str]:
    text = _combined_text(original_message, user_context)
    for channel in ["메일", "이메일", "문자", "카톡", "카카오톡", "DM", "디엠"]:
        if channel in text:
            return "이메일" if channel == "메일" else channel
    return None


class FeatureAnalysisAgent:
    def __init__(self, llm_client: LLMClientProtocol) -> None:
        self.llm_client = llm_client

    def __call__(self, state: MessagePolishingState) -> MessagePolishingState:
        original_message = state.get("original_message", "")
        user_feedback_message = state.get("user_feedback_message")
        user_context = state.get("user_context")
        relationship, recipient = analyze_relationship(original_message, user_context)
        heuristic_signals = {
            "intent": analyze_intent(original_message, user_feedback_message, user_context),
            "relationship": relationship,
            "recipient": recipient,
            "tone": analyze_tone(original_message, user_feedback_message, relationship),
            "communication_channel": _communication_channel(original_message, user_context),
            "extra_requests": analyze_extra_requests(user_feedback_message, original_message),
            "inferred_missing_info": analyze_missing_info(original_message, user_feedback_message),
        }
        payload = build_feature_analysis_payload(state, heuristic_signals)
        analysis = self.llm_client.generate_json(
            system_prompt=FEATURE_ANALYSIS_SYSTEM_PROMPT,
            user_payload=payload,
            response_schema=FeatureAnalysisResult,
            attachments=state.get("attachments"),
        )
        return {
            "analysis": analysis,
            "events": append_event(
                state,
                node="feature_analysis",
                message="Feature analysis completed.",
                details={"intent": analysis.intent, "confidence": analysis.confidence},
            ),
        }
