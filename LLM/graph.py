# app/graph.py
# Using LangGraph-style StateGraph API
from langgraph.graph import StateGraph, END
from app.state import OffboardingState
from app.agents.intent_agent_langchain import intent_agent
from app.agents.rag_agent_langchain import rag_agent
from app.agents.clarifier_agent_langchain import clarifier_agent
from app.agents.orchestrator_agent import orchestrator_agent

def decide_after_intent(state: OffboardingState):
    if state.pending_action is None:
        return "rag"
    if state.pending_action and state.missing_params:
        return "clarifier"
    return "orchestrator"

def decide_after_clarifier(state: OffboardingState):
    if state.missing_params:
        return "clarifier"
    return "orchestrator"

def build_graph():
    graph = StateGraph(OffboardingState)
    graph.add_node("intent", intent_agent)
    graph.add_node("rag", rag_agent)
    graph.add_node("clarifier", clarifier_agent)
    graph.add_node("orchestrator", orchestrator_agent)

    graph.set_entry_point("intent")

    graph.add_conditional_edges(
        "intent",
        decide_after_intent,
        {"rag": "rag", "clarifier": "clarifier", "orchestrator": "orchestrator"}
    )

    graph.add_conditional_edges(
        "clarifier",
        decide_after_clarifier,
        {"clarifier": "clarifier", "orchestrator": "orchestrator"}
    )

    graph.add_edge("orchestrator", END)
    return graph.compile()
