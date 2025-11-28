app/
 ├─ state.py
 ├─ graph.py                  <-- MAIN FILE (LangGraph workflow)
 ├─ agents/
 │   ├─ intent_agent.py       <-- LLM-based intent detection
 │   ├─ clarifier_agent.py
 │   ├─ rag_agent.py
 │   ├─ orchestrator_agent.py
 │   └─ service_agents.py
 ├─ schemas/
 │   └─ intent_schema.py
 ├─ prompts/
 │   └─ intent_prompt.py
 └─ adapters/
     └─ servicenow_adapter.py
