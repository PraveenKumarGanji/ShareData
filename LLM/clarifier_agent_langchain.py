# app/agents/clarifier_agent_langchain.py
from langchain import LLMChain, PromptTemplate
from app.langchain_setup import llm
from app.parsers.clarifier_parser import clarifier_parser

CLARIFIER_PROMPT = PromptTemplate(
    input_variables=["pending_action","known_params","missing_params","user_message"],
    template="""
You are a Clarifier Agent.
Given:
pending_action: {pending_action}
known_params: {known_params}
missing_params: {missing_params}
user_message: {user_message}

If the user_message provides the first missing param, extract it.
Otherwise ask a concise clarifying question for the first missing param.
Return JSON matching ClarifierOutput.
"""
)

clarifier_chain = LLMChain(llm=llm, prompt=CLARIFIER_PROMPT, output_parser=clarifier_parser)

async def clarifier_agent(state):
    # prepare inputs
    out = clarifier_chain.run(
        pending_action=state.pending_action,
        known_params=state.known_params,
        missing_params=state.missing_params,
        user_message=state.user_message
    )
    parsed = clarifier_parser.parse(out)
    if parsed.extracted_parameter_name and parsed.extracted_parameter_value:
        state.known_params[parsed.extracted_parameter_name] = parsed.extracted_parameter_value
        if parsed.extracted_parameter_name in state.missing_params:
            state.missing_params.remove(parsed.extracted_parameter_name)
        state.clarifier_question = None
        state.trace.append(f"Clarifier(LC): extracted {parsed.extracted_parameter_name}={parsed.extracted_parameter_value}")
    else:
        state.clarifier_question = parsed.question
        state.trace.append(f"Clarifier(LC): asked question `{parsed.question}`")
    return state
