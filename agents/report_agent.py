from rag.retriever import retrieve_documents
from utils.llm import ask_llm


def report_agent(query: str) -> str:

    # Retrieve relevant information from the documents
    documents = retrieve_documents(query, k=6)

    if not documents:
        return "I could not find relevant information in the documents."

    # Create context from retrieved documents
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

    # Ask the LLM to create a structured report
    prompt = f"""
You are a report generation agent.

Create a clear and well-structured report using ONLY
the information provided in the document context.

The report should contain:

1. Title
2. Introduction
3. Main Findings
4. Important Details
5. Conclusion
6. Sources / Page Numbers

Do not invent information that is not present in the context.

Document Context:
{context}

User Request:
{query}
"""

    report = ask_llm(prompt)

    return report