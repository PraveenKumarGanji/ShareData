# app/agents/intent_agent_langchain.py
from langchain import LLMChain, PromptTemplate
from app.langchain_setup import llm
from app.parsers.intent_parser import intent_parser
from app.prompts.intent_prompt_langchain import INTENT_PROMPT_TEMPLATE
from app.state import OffboardingState

prompt = PromptTemplate(
    template=INTENT_PROMPT_TEMPLATE,
    input_variables=["user_message"],
    partial_variables={"format_instructions": intent_parser.get_format_instructions()}
)
intent_chain = LLMChain(llm=llm, prompt=prompt, output_parser=intent_parser)

async def intent_agent(state: OffboardingState, user_message: str) -> OffboardingState:
    out = intent_chain.run(user_message=user_message)
    parsed = intent_parser.parse(out)
    state.pending_action = None if parsed.intent == "qa" else parsed.intent
    state.known_params = dict(parsed.provided_params or {})
    state.missing_params = list(parsed.missing_required_params or [])
    state.trace.append(f"IntentAgent: {parsed.intent} provided={parsed.provided_params} missing={parsed.missing_required_params}")
    return state
