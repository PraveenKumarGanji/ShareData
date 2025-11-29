# app/main.py
import uvicorn
from fastapi import FastAPI, Request
from typing import Dict
from app.state import OffboardingState
from app.graph_runner import SimpleGraphRunner

app = FastAPI(title="Offboarding LangChain LangGraph Demo")

SESSIONS: Dict[str, OffboardingState] = {}
runner = SimpleGraphRunner()

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

    result = await runner.run_turn(state, message)

    return {
        "type": result["type"],
        "assistant": result["assistant"],
        "state_trace": state.trace,
        "known_params": state.known_params,
        "missing_params": state.missing_params,
        "result": state.result
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
