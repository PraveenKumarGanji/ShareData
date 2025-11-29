# app/agents/clarifier_agent.py

import json
from openai import OpenAI
from app.state import OffboardingState
from app.schemas.clarifier_schema import CLARIFIER_SCHEMA
from app.prompts.clarifier_prompt import CLARIFIER_SYSTEM_PROMPT

client = OpenAI()

async def clarifier_agent(state: OffboardingState) -> OffboardingState:
    """
    LLM-based clarifier that:
    - decides if user message answers a missing field
    - or generates the next clarifying question
    - updates state.known_params and state.missing_params accordingly
    """

    # Prepare LLM messages
    missing = state.missing_params.copy()
    target_param = missing[0]  # Only extract one at a time

    # Build user context for LLM
    contextual_input = f"""
pending_action: {state.pending_action}
known_params: {state.known_params}
missing_params: {missing}
user_message: {state.user_message}
"""

    messages = [
        {"role": "system", "content": CLARIFIER_SYSTEM_PROMPT},
        {"role": "user", "content": contextual_input}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        functions=CLARIFIER_SCHEMA,
        function_call="auto"
    )

    msg = response.choices[0].message

    fn = msg.get("function_call")
    if fn is None:
        raise RuntimeError("LLM did not call clarify_parameter.")

    args = json.loads(fn["arguments"])
    question = args["question"]
    extracted_name = args["extracted_parameter_name"]
    extracted_value = args["extracted_parameter_value"]

    # CASE 1 — Extraction mode
    if extracted_name and extracted_value:
        # Update state
        state.known_params[extracted_name] = extracted_value
        if extracted_name in state.missing_params:
            state.missing_params.remove(extracted_name)

        state.trace.append(f"Clarifier: Extracted {extracted_name}={extracted_value}")
        state.clarifier_question = None  # No question to ask
        return state

    # CASE 2 — Question mode
    if question:
        state.trace.append(f"Clarifier: Asking question '{question}'")
        state.clarifier_question = question
        return state

    # If LLM produced empty fields by mistake
    raise RuntimeError("Clarifier LLM returned empty extraction and no question.")
