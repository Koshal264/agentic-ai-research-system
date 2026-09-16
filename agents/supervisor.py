from agents.document_agent import document_agent
from agents.report_agent import report_agent
from agents.research_agent import research_agent
from utils.llm import ask_llm


def supervisor_agent(query: str) -> str:

    # Decide which agent should handle the request
    decision_prompt = f"""
You are a supervisor agent.

Choose exactly one agent for the user's request.

DOCUMENT:
Use when the user asks a question about information
contained in the uploaded documents.

REPORT:
Use when the user asks for a report, structured report,
analysis, or detailed summary based on the documents.

RESEARCH:
Use for general knowledge, explanations, or research
questions that do not specifically require the uploaded
documents.

Reply with only one word:

DOCUMENT
REPORT
RESEARCH

User query:
{query}
"""

    decision = ask_llm(decision_prompt).strip().upper()

    if "REPORT" in decision:
        return report_agent(query)

    if "DOCUMENT" in decision:
        return document_agent(query)

    return research_agent(query)