# app/main.py
import uvicorn
from fastapi import FastAPI, Request
from typing import Dict
from app.state import OffboardingState
from app.runner import run_workflow

app = FastAPI(title="Offboarding with LangChain + LangGraph")

SESSIONS: Dict[str, OffboardingState] = {}

def get_session(session_id: str) -> OffboardingState:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = OffboardingState(session_id=session_id)
    return SESSIONS[session_id]

@app.post("/chat")
async def chat_endpoint(req: Request):
    body = await req.json()
    session_id = body.get("session_id", "default")
    user_id = body.get("user_id", "user")
    message = body.get("message", "")

    state = get_session(session_id)
    state.user_id = user_id

    final_state = await run_workflow(state, message)

    # The graph run will update state.trace, state.result, etc.
    return {
        "type": "done",
        "assistant": final_state.result if final_state.result else "OK",
        "state_trace": final_state.trace,
        "known_params": final_state.known_params,
        "missing_params": final_state.missing_params,
        "result": final_state.result
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
