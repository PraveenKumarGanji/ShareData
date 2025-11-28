# app/agents/rag_langchain.py
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from app.langchain_setup import llm, emb, vectorstore  # vectorstore built earlier

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k":4}),
    return_source_documents=True
)

async def rag_agent(state, user_message: str):
    # If you keep chat history for RAG, pass it; here we do a simple single-turn retrieval
    result = qa_chain({"question": user_message, "chat_history": []})
    state.retrieved_docs = [{"title": d.metadata.get("title","doc"), "text": d.page_content} for d in result.get("source_documents",[])]
    # result["answer"] is the LLM answer string — you may want to return it directly in QA path
    state.trace.append("RAGAgent(LC): retrieved docs")
    return state, result.get("answer")
