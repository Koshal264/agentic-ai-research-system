from rag.retriever import retrieve_documents
from utils.llm import ask_llm


def document_agent(query: str) -> str:

    # Get relevant information from the documents
    documents = retrieve_documents(query)

    if not documents:
        return "I could not find relevant information in the documents."

    # Prepare context from retrieved documents
    context_parts = []

    for document in documents:

        page = document.metadata.get("page")
        source = document.metadata.get("source")

        context_parts.append(
            f"""
Page: {page}
Source: {source}

Content:
{document.page_content}
"""
        )

    context = "\n\n".join(context_parts)

    # Create prompt for the LLM
    prompt = f"""
You are a document-based AI assistant.

Answer the user's question using only the information
provided in the document context below.

If the answer is not available in the context,
say that the information was not found in the documents.

Always mention the page number when possible.

Document Context:
{context}

User Question:
{query}
"""

    # Ask Gemini to generate the answer
    answer = ask_llm(prompt)

    return answer