# app/agents/clarifier_agent_langchain.py
from langchain import LLMChain, PromptTemplate
from app.langchain_setup import llm
from app.parsers.clarifier_parser import clarifier_parser
from app.prompts.clarifier_prompt_langchain import CLARIFIER_PROMPT_TEMPLATE
from app.state import OffboardingState

prompt = PromptTemplate(
    template=CLARIFIER_PROMPT_TEMPLATE,
    input_variables=["pending_action","known_params","missing_params","user_message"],
    partial_variables={"format_instructions": clarifier_parser.get_format_instructions()}
)
clarifier_chain = LLMChain(llm=llm, prompt=prompt, output_parser=clarifier_parser)

async def clarifier_agent(state: OffboardingState) -> OffboardingState:
    # run chain
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
        state.trace.append(f"ClarifierAgent: extracted {parsed.extracted_parameter_name}={parsed.extracted_parameter_value}")
    else:
        state.clarifier_question = parsed.question
        state.trace.append(f"ClarifierAgent: question='{parsed.question}'")
    return state
