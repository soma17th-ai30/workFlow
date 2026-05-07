"""
generate_user_feedback_message 단위 테스트

테스트 대상: agents/feedback.py::generate_user_feedback_message
역할: polished message와 analysis를 보고 부족한 정보를 사용자에게 안내하는 메시지 생성
"""

import pytest

from message_polishing.agents.feedback import generate_user_feedback_message
from message_polishing.schemas import FeatureAnalysisResult, MessagePolishingState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_full_analysis(**overrides) -> FeatureAnalysisResult:
    """relationship/recipient/intent/tone 모두 채운 기본 analysis 반환."""
    defaults = dict(
        intent="과제 제출 기한 연장 요청",
        relationship="학생→교수",
        recipient="교수님",
        tone="정중하고 공손하게",
    )
    defaults.update(overrides)
    return FeatureAnalysisResult(**defaults)


def _make_state(
    *,
    analysis: FeatureAnalysisResult | None = None,
    polished_message: str = "안녕하세요. 과제 제출 기한을 연장해 주실 수 있을까요?",
) -> MessagePolishingState:
    return MessagePolishingState(
        original_message="교수님, 과제 제출이 어렵습니다.",
        current_polished_message=polished_message,
        analysis=analysis,
    )


# ---------------------------------------------------------------------------
# 케이스 1 - 모든 정보가 있는 경우
# ---------------------------------------------------------------------------

class TestAllInfoPresent:
    def test_returns_none_when_analysis_complete_and_no_placeholders(self):
        """analysis 필드 모두 채워지고 플레이스홀더 없으면 feedbackMessage는 None이어야 한다."""
        state = _make_state(analysis=_make_full_analysis())
        result = generate_user_feedback_message(state)
        assert result is None


# ---------------------------------------------------------------------------
# 케이스 2 - 관계 정보 없는 경우
# ---------------------------------------------------------------------------

class TestMissingRelationship:
    def test_includes_relationship_hint(self):
        """analysis.relationship=None이면 '상대방과의 관계'가 메시지에 포함되어야 한다."""
        state = _make_state(analysis=_make_full_analysis(relationship=None))
        result = generate_user_feedback_message(state)
        assert result is not None
        assert "상대방과의 관계" in result

    def test_message_ends_with_guidance_phrase(self):
        """안내 문구가 자연스럽게 마무리되어야 한다."""
        state = _make_state(analysis=_make_full_analysis(relationship=None))
        result = generate_user_feedback_message(state)
        assert result is not None
        assert "알려주시면" in result
        assert "만들 수 있어요" in result


# ---------------------------------------------------------------------------
# 케이스 3 - 플레이스홀더가 있는 경우
# ---------------------------------------------------------------------------

class TestPlaceholderInMessage:
    def test_includes_placeholder_text(self):
        """polished_message에 [희망기한]이 있으면 '희망기한'이 feedbackMessage에 포함되어야 한다."""
        state = _make_state(
            analysis=_make_full_analysis(),
            polished_message="[희망기한]까지 제출하겠습니다.",
        )
        result = generate_user_feedback_message(state)
        assert result is not None
        assert "희망기한" in result

    def test_multiple_placeholders_all_included(self):
        """여러 플레이스홀더가 모두 feedbackMessage에 포함되어야 한다."""
        state = _make_state(
            analysis=_make_full_analysis(),
            polished_message="[희망기한]까지 [사유]로 인해 제출이 어렵습니다.",
        )
        result = generate_user_feedback_message(state)
        assert result is not None
        assert "희망기한" in result
        assert "사유" in result

    def test_no_duplicate_hints(self):
        """같은 플레이스홀더가 중복으로 등장해도 feedbackMessage에 한 번만 포함되어야 한다."""
        state = _make_state(
            analysis=_make_full_analysis(),
            polished_message="[희망기한] 이후 [희망기한] 재확인",
        )
        result = generate_user_feedback_message(state)
        assert result is not None
        assert result.count("희망기한") == 1


# ---------------------------------------------------------------------------
# 케이스 4 - 모든 정보가 없는 경우 (analysis 필드 전부 None)
# ---------------------------------------------------------------------------

class TestAllFieldsMissing:
    def test_message_contains_multiple_hints(self):
        """relationship/recipient/intent/tone 모두 None이면 feedbackMessage에 여러 항목이 포함되어야 한다."""
        state = _make_state(
            analysis=_make_full_analysis(
                relationship=None,
                recipient=None,
                intent=None,
                tone=None,
            )
        )
        result = generate_user_feedback_message(state)
        assert result is not None
        hint_keywords = ["상대방과의 관계", "메시지 수신자", "메시지의 목적", "원하시는 말투나 톤"]
        matched = [kw for kw in hint_keywords if kw in result]
        assert len(matched) >= 2, f"최소 2개 이상의 힌트가 포함되어야 하지만 실제: {result!r}"

    def test_message_is_not_empty_string(self):
        state = _make_state(
            analysis=_make_full_analysis(
                relationship=None, recipient=None, intent=None, tone=None
            )
        )
        result = generate_user_feedback_message(state)
        assert result  # None도 아니고 빈 문자열도 아니어야 한다


# ---------------------------------------------------------------------------
# 케이스 5 - analysis 자체가 None인 경우
# ---------------------------------------------------------------------------

class TestAnalysisIsNone:
    def test_does_not_raise(self):
        """state에 analysis가 없어도 예외 없이 처리되어야 한다."""
        state = _make_state(analysis=None)
        result = generate_user_feedback_message(state)
        # analysis가 None이면 analysis 기반 힌트는 없고, 플레이스홀더도 없으므로 None 반환
        assert result is None

    def test_does_not_raise_with_missing_analysis_key(self):
        """MessagePolishingState에 analysis 키 자체가 없어도 예외 없이 처리되어야 한다."""
        state: MessagePolishingState = MessagePolishingState(
            original_message="테스트",
            current_polished_message="다듬어진 메시지입니다.",
        )
        result = generate_user_feedback_message(state)
        assert result is None


# ---------------------------------------------------------------------------
# 케이스 6 - 빈 메시지인 경우
# ---------------------------------------------------------------------------

class TestEmptyPolishedMessage:
    def test_empty_message_does_not_raise(self):
        """polished_message=""여도 예외 없이 처리되어야 한다."""
        state = _make_state(analysis=_make_full_analysis(), polished_message="")
        result = generate_user_feedback_message(state)
        assert result is None  # 플레이스홀더 없고 analysis 완전하면 None

    def test_none_polished_message_does_not_raise(self):
        """current_polished_message가 None이어도 예외 없이 처리되어야 한다."""
        state: MessagePolishingState = MessagePolishingState(
            original_message="테스트",
            current_polished_message=None,
            analysis=_make_full_analysis(),
        )
        result = generate_user_feedback_message(state)
        assert result is None
