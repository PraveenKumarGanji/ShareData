# app/runner.py
from app.graph import build_graph
from app.state import OffboardingState

GRAPH = build_graph()

async def run_workflow(state: OffboardingState, user_message: str):
    """
    Execute the LangGraph workflow for a single turn.
    GRAPH.execute expects the graph runtime API; adapt if library differs.
    """
    # set the user's latest message into state so clarifier can access
    state.user_message = user_message

    # Execute graph - exact API depends on langgraph package.
    # Here we assume compiled graph has a .run(state) coroutine that returns final state and terminal node.
    result = await GRAPH.run(state)  # if your library uses .execute or .call, adapt accordingly

    # result may be final state object; return state for caller
    return result
