from rag.retriever import retrieve_documents
from utils.llm import ask_llm


def compliance_agent(
    query: str,
    source: str = None
) -> str:

    # ==========================================
    # 1. CHECK SOURCE
    # ==========================================

    if not source:
        return (
            "Please upload a relevant policy, regulation, "
            "or compliance document so I can perform "
            "a grounded compliance analysis."
        )

    # ==========================================
    # 2. RETRIEVE RELEVANT DOCUMENTS
    # ==========================================

    documents = retrieve_documents(
        query=query,
        k=4,
        source=source
    )

    if not documents:
        return (
            f"I could not find relevant compliance "
            f"information in the uploaded document: {source}"
        )

    # ==========================================
    # 3. BUILD CONTEXT
    # ==========================================

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

    # ==========================================
    # 4. COMPLIANCE PROMPT
    # ==========================================

    prompt = f"""
You are a Compliance AI Agent inside
Sovereign AI Workbench.

Your job is to analyze compliance-related
requirements using the provided documents.

You can help with:

- Policy compliance
- Regulatory requirements
- Security requirements
- Privacy requirements
- Audit requirements
- Data protection requirements
- Compliance gaps
- Compliance checklists
- Identifying documented obligations

IMPORTANT RULES:

1. Use ONLY the provided document context.
2. Do not invent laws, regulations, policies,
   requirements, or penalties.
3. Clearly distinguish documented requirements
   from general recommendations.
4. Mention page numbers when possible.
5. If the requested information is not present
   in the document, clearly say so.
6. Do not present assumptions as facts.
7. If the document is insufficient to determine
   compliance, clearly mention what information
   is missing.
8. Keep the response structured and easy to understand.

Document Context:
{context}

User Query:
{query}
"""

    # ==========================================
    # 5. GENERATE ANSWER
    # ==========================================

    answer = ask_llm(prompt)

    return answer