from __future__ import annotations

from typing import Any, Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from message_polishing.agents import FeatureAnalysisAgent, FeedbackAgent, PolishingAgent
from message_polishing.context import (
    InMemorySessionStore,
    SessionStoreProtocol,
    build_applied_feedback_summary,
    build_debug_payload,
    build_session_snapshot,
    make_initial_state,
)
from message_polishing.llm import LLMClientProtocol, UpstageResponsesClient
from message_polishing.schemas import (
    FeedbackResult,
    MessagePolishingInput,
    MessagePolishingOutput,
    MessagePolishingState,
    coerce_model,
)
from message_polishing.settings import MessagePolishingSettings


_DEFAULT_SESSION_STORE = InMemorySessionStore()
_DEFAULT_CHECKPOINTER = MemorySaver()


def should_revise(state: MessagePolishingState, *, max_feedback_iterations: int = 2) -> str:
    feedback_result = coerce_model(state.get("feedback_result"), FeedbackResult)
    if (
        feedback_result
        and feedback_result.revision_needed
        and int(state.get("feedback_iteration", 0)) < max_feedback_iterations
    ):
        return "revise"
    return "end"


def build_graph(
    *,
    llm_client: Optional[LLMClientProtocol] = None,
    settings: Optional[MessagePolishingSettings] = None,
    checkpointer: Any = None,
):
    settings = settings or MessagePolishingSettings.from_env()
    llm_client = llm_client or UpstageResponsesClient(settings)

    feature_analysis_agent = FeatureAnalysisAgent(llm_client)
    polishing_agent = PolishingAgent(llm_client)
    feedback_agent = FeedbackAgent(llm_client)

    graph_builder = StateGraph(MessagePolishingState)
    graph_builder.add_node("feature_analysis", feature_analysis_agent)
    graph_builder.add_node("polishing", polishing_agent)
    graph_builder.add_node("feedback", feedback_agent)

    graph_builder.add_edge(START, "feature_analysis")
    graph_builder.add_edge("feature_analysis", "polishing")
    graph_builder.add_edge("polishing", "feedback")
    graph_builder.add_conditional_edges(
        "feedback",
        lambda state: should_revise(state, max_feedback_iterations=settings.max_feedback_iterations),
        {
            "revise": "polishing",
            "end": END,
        },
    )
    return graph_builder.compile(checkpointer=checkpointer)


def run_message_polishing_workflow(
    input: MessagePolishingInput | dict[str, Any],
    *,
    debug: bool = False,
) -> MessagePolishingOutput:
    return run_message_polishing_workflow_with_client(input, debug=debug)


def run_message_polishing_workflow_with_client(
    input: MessagePolishingInput | dict[str, Any],
    *,
    debug: bool = False,
    llm_client: Optional[LLMClientProtocol] = None,
    settings: Optional[MessagePolishingSettings] = None,
    session_store: Optional[SessionStoreProtocol] = None,
    checkpointer: Any = None,
) -> MessagePolishingOutput:
    workflow_input = (
        input if isinstance(input, MessagePolishingInput) else MessagePolishingInput.model_validate(input)
    )
    settings = settings or MessagePolishingSettings.from_env()
    session_store = session_store or _DEFAULT_SESSION_STORE

    persisted_snapshot = (
        session_store.load(workflow_input.sessionId)
        if workflow_input.sessionId
        else None
    )
    initial_state = make_initial_state(workflow_input, persisted_snapshot=persisted_snapshot)

    effective_checkpointer = checkpointer
    config = None
    if workflow_input.sessionId:
        effective_checkpointer = _DEFAULT_CHECKPOINTER if effective_checkpointer is None else effective_checkpointer
        config = {"configurable": {"thread_id": workflow_input.sessionId}}

    graph = build_graph(
        llm_client=llm_client,
        settings=settings,
        checkpointer=effective_checkpointer,
    )
    final_state = graph.invoke(initial_state, config=config)

    polished_message = final_state.get("current_polished_message")
    if not polished_message:
        raise RuntimeError("Message polishing workflow finished without a polished message.")

    if workflow_input.sessionId:
        session_store.save(workflow_input.sessionId, build_session_snapshot(final_state))

    return MessagePolishingOutput(
        polishedMessage=polished_message,
        appliedFeedbackSummary=build_applied_feedback_summary(final_state),
        debug=build_debug_payload(final_state) if debug else None,
    )
