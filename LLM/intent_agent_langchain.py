from langchain.chat_models import ChatOpenAI
from langchain import LLMChain, PromptTemplate

from app.parsers.intent_parser import intent_parser
from app.prompts.intent_prompt_langchain import INTENT_PROMPT_TEMPLATE
from app.state import OffboardingState

import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 1) Create LLM instance (can switch model easily)
llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

# 2) Build prompt with parser instructions
prompt = PromptTemplate(
    template=INTENT_PROMPT_TEMPLATE,
    input_variables=["user_message"],
    partial_variables={"format_instructions": intent_parser.get_format_instructions()}
)

# 3) Construct chain
intent_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    output_parser=intent_parser
)

# 4) Intent Agent Function
async def intent_agent(state: OffboardingState, user_message: str) -> OffboardingState:
    """
    LangChain-powered Intent Agent.
    Runs the Intent Chain -> gets structured IntentOutput -> updates LangGraph state.
    """

    # Call the LLM chain (sync for now; wrap later if needed)
    output = intent_chain.run(user_message=user_message)

    # Parse into structured Pydantic model
    parsed = intent_parser.parse(output)

    # Apply to state
    state.pending_action = None if parsed.intent == "qa" else parsed.intent
    state.known_params = dict(parsed.provided_params)
    state.missing_params = list(parsed.missing_required_params)

    state.trace.append(
        f"IntentAgent(LC): intent={parsed.intent}, provided={parsed.provided_params}, missing={parsed.missing_required_params}"
    )

    return state
