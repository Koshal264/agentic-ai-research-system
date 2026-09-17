
from rag.retriever import retrieve_documents
from utils.llm import ask_llm


def report_agent(
    query: str,
    source: str = None
) -> str:

    documents = retrieve_documents(
        query=query,
        k=6,
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
You are a professional report generation agent.

Create a clear and well-structured report using
ONLY the information provided in the document context.

Selected PDF:
{source}

The report must contain:

1. Title
2. Introduction
3. Main Findings
4. Important Details
5. Conclusion
6. Sources / Page Numbers

IMPORTANT RULES:

- Use ONLY the selected PDF context.
- Do NOT use information from another PDF.
- Do NOT invent facts.
- Mention relevant page numbers.
- If something is not available in the context,
  do not make it up.

Document Context:
{context}

User Request:
{query}
"""

    report = ask_llm(prompt)

    return report

