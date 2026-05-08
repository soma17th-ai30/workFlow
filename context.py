from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional, Protocol

from pydantic import BaseModel

from message_polishing.schemas import (
    FeatureAnalysisResult,
    FeedbackResult,
    MessagePolishingInput,
    MessagePolishingState,
    PolishingValidationResult,
    WorkflowEvent,
    coerce_model,
    dump_model,
)


class SessionStoreProtocol(Protocol):
    def load(self, session_id: str) -> dict[str, Any] | None:
        ...

    def save(self, session_id: str, snapshot: dict[str, Any]) -> None:
        ...


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    def load(self, session_id: str) -> dict[str, Any] | None:
        return self._sessions.get(session_id)

    def save(self, session_id: str, snapshot: dict[str, Any]) -> None:
        self._sessions[session_id] = snapshot


def model_to_payload(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    return dump_model(value)


def make_event(node: str, message: str, details: Optional[dict[str, Any]] = None) -> WorkflowEvent:
    return WorkflowEvent(
        node=node,
        message=message,
        details=details or {},
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def append_event(
    state: MessagePolishingState,
    *,
    node: str,
    message: str,
    details: Optional[dict[str, Any]] = None,
) -> list[WorkflowEvent | dict[str, Any]]:
    events = list(state.get("events") or [])
    events.append(make_event(node, message, details))
    return events


def make_initial_state(
    workflow_input: MessagePolishingInput,
    *,
    persisted_snapshot: Optional[dict[str, Any]] = None,
) -> MessagePolishingState:
    persisted_snapshot = persisted_snapshot or {}
    previous_polished_message = (
        workflow_input.previousPolishedMessage
        or persisted_snapshot.get("previous_polished_message")
    )
    context_summary = persisted_snapshot.get("context_summary")

    return MessagePolishingState(
        original_message=workflow_input.originalMessage.strip(),
        user_feedback_message=(
            workflow_input.feedbackMessage.strip()
            if isinstance(workflow_input.feedbackMessage, str) and workflow_input.feedbackMessage.strip()
            else None
        ),
        user_context=workflow_input.userContext,
        session_id=workflow_input.sessionId,
        context_summary=context_summary,
        attachments=workflow_input.attachments,
        previous_polished_message=previous_polished_message,
        current_polished_message=None,
        analysis=None,
        polishing_validation=None,
        feedback_result=None,
        revision_instruction=None,
        feedback_iteration=0,
        events=[],
    )


def build_feature_analysis_payload(state: MessagePolishingState, heuristic_signals: dict[str, Any]) -> dict[str, Any]:
    return {
        "original_message": state.get("original_message"),
        "user_feedback_message": state.get("user_feedback_message"),
        "user_context": state.get("user_context"),
        "context_summary": state.get("context_summary"),
        "previous_polished_message": state.get("previous_polished_message"),
        "previous_analysis": model_to_payload(state.get("analysis")),
        "heuristic_signals": heuristic_signals,
    }


def build_polishing_payload(state: MessagePolishingState) -> dict[str, Any]:
    return {
        "original_message": state.get("original_message"),
        "user_feedback_message": state.get("user_feedback_message"),
        "user_context": state.get("user_context"),
        "context_summary": state.get("context_summary"),
        "analysis": model_to_payload(state.get("analysis")),
        "previous_polished_message": state.get("previous_polished_message"),
        "current_polished_message": state.get("current_polished_message"),
        "revision_instruction": state.get("revision_instruction"),
    }


def build_feedback_payload(state: MessagePolishingState, feedback_items: list[str]) -> dict[str, Any]:
    return {
        "original_message": state.get("original_message"),
        "user_feedback_message": state.get("user_feedback_message"),
        "user_context": state.get("user_context"),
        "context_summary": state.get("context_summary"),
        "analysis": model_to_payload(state.get("analysis")),
        "previous_polished_message": state.get("previous_polished_message"),
        "current_polished_message": state.get("current_polished_message"),
        "polishing_validation": model_to_payload(state.get("polishing_validation")),
        "feedback_items": feedback_items,
    }


def update_context_summary(state: MessagePolishingState) -> str:
    analysis = coerce_model(state.get("analysis"), FeatureAnalysisResult)
    feedback_result = coerce_model(state.get("feedback_result"), FeedbackResult)

    recent_feedback: list[str] = []
    if feedback_result:
        recent_feedback.extend(feedback_result.applied_feedback_items)
        recent_feedback.extend(feedback_result.unresolved_feedback_items)
    elif state.get("user_feedback_message"):
        recent_feedback.append(str(state.get("user_feedback_message")))

    summary = {
        "last_intent": analysis.intent if analysis else None,
        "last_relationship": analysis.relationship if analysis else None,
        "last_situation": analysis.situation if analysis else None,
        "last_recipient": analysis.recipient if analysis else None,
        "last_current_speech_level": analysis.current_speech_level if analysis else None,
        "last_speech_level": analysis.speech_level if analysis else None,
        "last_current_tone": analysis.current_tone if analysis else None,
        "last_tone": analysis.tone if analysis else None,
        "last_polished_message": state.get("current_polished_message"),
        "recent_user_feedback": recent_feedback[-5:],
    }
    return json.dumps(summary, ensure_ascii=False)


def build_session_snapshot(state: MessagePolishingState) -> dict[str, Any]:
    return {
        "original_message": state.get("original_message"),
        "context_summary": update_context_summary(state),
        "previous_polished_message": state.get("current_polished_message"),
        "analysis": model_to_payload(state.get("analysis")),
    }


def build_applied_feedback_summary(state: MessagePolishingState) -> Optional[str]:
    if not state.get("user_feedback_message"):
        return None

    feedback_result = coerce_model(state.get("feedback_result"), FeedbackResult)
    if not feedback_result:
        return "요청하신 피드백을 반영했습니다."

    applied_items = feedback_result.applied_feedback_items
    unresolved_items = feedback_result.unresolved_feedback_items
    if applied_items and not unresolved_items:
        return f"다음 피드백을 반영했습니다: {', '.join(applied_items)}"
    if applied_items:
        return f"다음 피드백을 반영했고, 나머지는 가능한 범위에서 조정했습니다: {', '.join(applied_items)}"
    return "요청하신 피드백을 가능한 범위에서 반영했습니다."


def build_debug_payload(state: MessagePolishingState) -> dict[str, Any]:
    analysis = coerce_model(state.get("analysis"), FeatureAnalysisResult)
    validation = coerce_model(state.get("polishing_validation"), PolishingValidationResult)
    feedback_result = coerce_model(state.get("feedback_result"), FeedbackResult)
    events = [model_to_payload(event) for event in state.get("events") or []]
    return {
        "analysis": model_to_payload(analysis),
        "polishing_validation": model_to_payload(validation),
        "feedback_result": model_to_payload(feedback_result),
        "feedback_iteration": state.get("feedback_iteration", 0),
        "events": events,
    }
