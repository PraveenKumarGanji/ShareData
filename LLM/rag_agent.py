# app/agents/rag_agent_langchain.py
from app.langchain_setup import build_vectorstore_from_texts, llm
from app.state import OffboardingState
from langchain.chains import RetrievalQA

# simple demo docs; in prod load policy docs
DEMO_DOCS = [
    "Asset Return Policy: Employees must return assets within 3 business days.",
    "Offboarding Checklist: 1) Update Workday 2) Revoke access 3) Asset return 4) Payroll settlement"
]

# Build vectorstore on startup
vectorstore = build_vectorstore_from_texts(DEMO_DOCS)

# Build Retrieval QA chain
if vectorstore:
    retriever = vectorstore.as_retriever(search_kwargs={"k":3})
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

async def rag_agent(state: OffboardingState, user_message: str) -> (OffboardingState, str):
    if not vectorstore:
        state.trace.append("RAGAgent: no vectorstore")
        return state, "No policy docs available."
    result = qa_chain.run(user_message)
    state.retrieved_docs = [{"text": d.page_content} for d in retriever.get_relevant_documents(user_message)]
    state.trace.append("RAGAgent: ran QA chain")
    return state, result
