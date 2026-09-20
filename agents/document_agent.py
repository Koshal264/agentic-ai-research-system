from rag.retriever import retrieve_documents
from utils.llm import ask_llm


def document_agent(
    query: str,
    source: str = None
) -> str:

    documents = retrieve_documents(
        query=query,
        k=4,
        source=source
    )

    if not documents:

        if source:
            return (
                f"I could not find relevant information "
                f"in the uploaded PDF: {source}"
            )

        return (
            "I could not find relevant information "
            "in the documents."
        )

    context_parts = []

    for document in documents:

        page = document.metadata.get("page")
        pdf_source = document.metadata.get("source")

        context_parts.append(
            f"""
Page: {page}
Source: {pdf_source}

Content:
{document.page_content}
"""
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a document-based AI assistant.

Answer the user's question using ONLY the
information provided in the document context.

The selected PDF is:

{source}

IMPORTANT RULES:

1. Use only the provided document context.
2. Do not use information from other PDFs.
3. Do not invent information.
4. Mention page numbers when possible.
5. If the answer is not present in the context,
   clearly say that it was not found.

Document Context:
{context}

User Question:
{query}
"""

    answer = ask_llm(prompt)

    return answer