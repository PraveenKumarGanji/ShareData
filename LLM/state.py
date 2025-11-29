# app/state.py
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class OffboardingState(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[str] = None

    pending_action: Optional[str] = None
    known_params: Dict[str, Any] = {}
    missing_params: List[str] = []

    user_message: Optional[str] = None
    clarifier_question: Optional[str] = None

    retrieved_docs: List[Dict[str, Any]] = []
    result: Optional[Dict[str, Any]] = None
    trace: List[str] = []
