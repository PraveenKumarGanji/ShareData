# app/graph.py

from langgraph.graph import StateGraph, END

from app.state import OffboardingState
from app.agents.intent_agent import intent_agent
from app.agents.rag_agent import rag_agent
from app.agents.clarifier_agent import clarifier_agent, merge_user_answer
from app.agents.orchestrator_agent import orchestrator_agent


# ---------------------------
# CONDITIONAL NODE FUNCTIONS
# ---------------------------

def decide_next_step(state: OffboardingState):
    """
    Decide next graph node based on:
    1. Intent = 'qa' → go to RAG agent
    2. Action with missing fields → clarifier
    3. Action with complete fields → orchestrator
    """
    if state.pending_action is None:
        return "rag"

    if state.pending_action and state.missing_params:
        return "clarifier"

    return "orchestrator"


def should_finish(state: OffboardingState):
    """Orchestrator always leads to END."""
    return END


# ---------------------------
# GRAPH DEFINITION
# ---------------------------

def build_graph():
    graph = StateGraph(OffboardingState)

    # Entry: always run intent agent first
    graph.add_node("intent", intent_agent)

    # Q&A Node
    graph.add_node("rag", rag_agent)

    # Clarifier Node
    graph.add_node("clarifier", clarifier_agent)

    # Orchestrator Node
    graph.add_node("orchestrator", orchestrator_agent)

    # Entry point
    graph.set_entry_point("intent")

    # Conditional branching after intent agent
    graph.add_conditional_edges(
        "intent",
        decide_next_step,
        {
            "rag": "rag",
            "clarifier": "clarifier",
            "orchestrator": "orchestrator"
        }
    )

    # Clarifier leads back to itself until all params collected
    graph.add_conditional_edges(
        "clarifier",
        lambda state: "clarifier" if state.missing_params else "orchestrator",
        {
            "clarifier": "clarifier",
            "orchestrator": "orchestrator"
        }
    )

    # Orchestrator → END
    graph.add_edge("orchestrator", END)

    return graph.compile()
