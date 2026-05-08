from __future__ import annotations

from message_polishing.context import append_event, build_feature_analysis_payload
from message_polishing.llm import LLMClientProtocol
from message_polishing.prompts import FEATURE_ANALYSIS_SYSTEM_PROMPT
from message_polishing.schemas import FeatureAnalysisResult, MessagePolishingState


class FeatureAnalysisAgent:
    def __init__(self, llm_client: LLMClientProtocol) -> None:
        self.llm_client = llm_client

    def __call__(self, state: MessagePolishingState) -> MessagePolishingState:
        payload = build_feature_analysis_payload(state, heuristic_signals={})
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
