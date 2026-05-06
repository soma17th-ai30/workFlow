from __future__ import annotations

from typing import Any, Optional, TypeVar, TypedDict

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)


class MessagePolishingBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AttachmentInput(MessagePolishingBaseModel):
    path: Optional[str] = None
    fileId: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("fileId", "file_id"),
        serialization_alias="fileId",
    )
    mimeType: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("mimeType", "mime_type"),
        serialization_alias="mimeType",
    )


class MessagePolishingInput(MessagePolishingBaseModel):
    originalMessage: str = Field(
        validation_alias=AliasChoices("originalMessage", "original_message"),
        serialization_alias="originalMessage",
        min_length=1,
    )
    feedbackMessage: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("feedbackMessage", "feedback_message"),
        serialization_alias="feedbackMessage",
    )
    previousPolishedMessage: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("previousPolishedMessage", "previous_polished_message"),
        serialization_alias="previousPolishedMessage",
    )
    userContext: Optional[dict[str, Any] | str] = Field(
        default=None,
        validation_alias=AliasChoices("userContext", "user_context"),
        serialization_alias="userContext",
    )
    sessionId: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("sessionId", "session_id"),
        serialization_alias="sessionId",
    )
    attachments: Optional[list[AttachmentInput]] = None


class WorkflowEvent(MessagePolishingBaseModel):
    node: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class FeatureAnalysisResult(MessagePolishingBaseModel):
    intent: Optional[str] = None
    relationship: Optional[str] = None
    recipient: Optional[str] = None
    tone: Optional[str] = None
    communication_channel: Optional[str] = None
    constraints: list[str] = Field(default_factory=list)
    extra_requests: list[str] = Field(default_factory=list)
    inferred_missing_info: list[str] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    @model_validator(mode="before")
    @classmethod
    def drop_extra_llm_fields(cls, value: Any) -> Any:
        return keep_allowed_fields(
            value,
            {
                "intent",
                "relationship",
                "recipient",
                "tone",
                "communication_channel",
                "constraints",
                "extra_requests",
                "inferred_missing_info",
                "risk_notes",
                "confidence",
            },
        )


class PolishingValidationResult(MessagePolishingBaseModel):
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    checks: dict[str, bool] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_llm_validation_payload(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        normalized = keep_allowed_fields(value, {"passed", "score", "issues", "checks"})
        critical_issues = value.get("critical_issues")
        if critical_issues:
            existing_issues = list(normalized.get("issues") or [])
            if isinstance(critical_issues, list):
                existing_issues.extend(str(issue) for issue in critical_issues)
            else:
                existing_issues.append(str(critical_issues))
            normalized["issues"] = list(dict.fromkeys(existing_issues))

        if "passed" not in normalized:
            score = normalized.get("score")
            checks = normalize_boolean_checks(normalized.get("checks", {}))
            issues = normalized.get("issues") or []
            normalized["passed"] = (
                isinstance(score, (int, float))
                and float(score) >= 0.75
                and not issues
                and all(checks.values())
            )
        return normalized

    @field_validator("checks", mode="before")
    @classmethod
    def keep_boolean_checks(cls, value: Any) -> Any:
        return normalize_boolean_checks(value)


class PolishingResult(MessagePolishingBaseModel):
    polished_message: str
    validation: PolishingValidationResult
    revision_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def drop_extra_llm_fields(cls, value: Any) -> Any:
        return keep_allowed_fields(value, {"polished_message", "validation", "revision_notes"})


class FeedbackResult(MessagePolishingBaseModel):
    feedback_satisfied: bool
    revision_needed: bool
    revision_instruction: Optional[str] = None
    unresolved_feedback_items: list[str] = Field(default_factory=list)
    applied_feedback_items: list[str] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)
    checks: dict[str, bool] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def drop_extra_llm_fields(cls, value: Any) -> Any:
        return keep_allowed_fields(
            value,
            {
                "feedback_satisfied",
                "revision_needed",
                "revision_instruction",
                "unresolved_feedback_items",
                "applied_feedback_items",
                "score",
                "issues",
                "checks",
            },
        )

    @field_validator("checks", mode="before")
    @classmethod
    def keep_boolean_checks(cls, value: Any) -> Any:
        return normalize_boolean_checks(value)


class MessagePolishingOutput(MessagePolishingBaseModel):
    polishedMessage: str = Field(
        validation_alias=AliasChoices("polishedMessage", "polished_message"),
        serialization_alias="polishedMessage",
    )
    appliedFeedbackSummary: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("appliedFeedbackSummary", "applied_feedback_summary"),
        serialization_alias="appliedFeedbackSummary",
    )
    debug: Optional[dict[str, Any]] = None


class MessagePolishingState(TypedDict, total=False):
    original_message: str
    user_feedback_message: Optional[str]
    user_context: Optional[dict[str, Any] | str]
    session_id: Optional[str]
    context_summary: Optional[str]
    attachments: Optional[list[AttachmentInput]]

    previous_polished_message: Optional[str]
    current_polished_message: Optional[str]

    analysis: Optional[FeatureAnalysisResult | dict[str, Any]]
    polishing_validation: Optional[PolishingValidationResult | dict[str, Any]]

    feedback_result: Optional[FeedbackResult | dict[str, Any]]
    revision_instruction: Optional[str]
    feedback_iteration: int

    events: list[WorkflowEvent | dict[str, Any]]


def coerce_model(value: Any, model_type: type[TBaseModel]) -> Optional[TBaseModel]:
    if value is None:
        return None
    if isinstance(value, model_type):
        return value
    return model_type.model_validate(value)


def normalize_boolean_checks(value: Any) -> Any:
    if not isinstance(value, dict):
        return value

    normalized: dict[str, bool] = {}
    for key, item in value.items():
        if isinstance(item, bool):
            normalized[str(key)] = item
        elif isinstance(item, str) and item.lower() in {"true", "false"}:
            normalized[str(key)] = item.lower() == "true"
    return normalized


def keep_allowed_fields(value: Any, allowed_fields: set[str]) -> Any:
    if not isinstance(value, dict):
        return value
    return {key: item for key, item in value.items() if key in allowed_fields}


def dump_model(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [dump_model(item) for item in value]
    if isinstance(value, dict):
        return {key: dump_model(item) for key, item in value.items()}
    return value
