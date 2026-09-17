
from agents.document_agent import document_agent
from agents.report_agent import report_agent
from agents.research_agent import research_agent
from agents.vision_agent import vision_agent
from utils.llm import ask_llm


def supervisor_agent(
    query: str,
    image_path: str = None,
    source: str = None
) -> str:

    # ========================================
    # VISION AGENT
    # ========================================

    if image_path:

        return vision_agent(
            image_path=image_path,
            query=query
        )


    # ========================================
    # TEXT-BASED SUPERVISOR
    # ========================================

    decision_prompt = f"""
You are a supervisor agent.

Choose exactly one agent for the user's request.

DOCUMENT:

Use when the user asks a question about
information contained in the uploaded PDF.

REPORT:

Use when the user asks for a report, structured
report, analysis, or detailed summary based on
the uploaded PDF.

RESEARCH:

Use for general knowledge, explanations, or
research questions that do not require the
uploaded PDF.

IMPORTANT:

If a PDF has been uploaded and the user's question
refers to "this PDF", "this document", "the uploaded
PDF", or asks to make a report of it, choose:

DOCUMENT or REPORT

Do NOT choose RESEARCH in these cases.

Reply with only one word:

DOCUMENT
REPORT
RESEARCH

Selected PDF:
{source}

User query:
{query}
"""


    decision = ask_llm(
        decision_prompt
    ).strip().upper()


    print("========================================")
    print("SUPERVISOR DECISION")
    print("Query:", query)
    print("PDF:", source)
    print("Decision:", decision)
    print("========================================")


    # ========================================
    # ROUTING
    # ========================================

    if "REPORT" in decision:

        return report_agent(
            query=query,
            source=source
        )


    if "DOCUMENT" in decision:

        return document_agent(
            query=query,
            source=source
        )


    return research_agent(
        query
    
    )