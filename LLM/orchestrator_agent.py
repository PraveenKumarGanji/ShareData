# app/agents/orchestrator_agent.py
from app.state import OffboardingState
from app.adapters.servicenow_adapter import servicenow

async def orchestrator_agent(state: OffboardingState) -> OffboardingState:
    action = state.pending_action
    params = state.known_params.copy()
    state.trace.append(f"Orchestrator: executing {action} with {params}")

    if action == "create_asset_return":
        employee_id = params.get("employee_id")
        asset_type = params.get("asset_type")
        pickup_date = params.get("pickup_date")
        if not employee_id:
            raise ValueError("employee_id required")
        short = f"Asset return: {asset_type} for {employee_id}"
        comments = f"Pickup: {pickup_date}"
        ticket = servicenow.create_incident(short_description=short, caller_id=employee_id, comments=comments)
        state.result = {"ticket": ticket}
        state.trace.append(f"Orchestrator: created ticket {ticket['number']}")
        return state

    state.result = {"status": "unknown_action"}
    return state
