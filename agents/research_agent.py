from utils.llm import ask_llm


def research_agent(query: str) -> str:

    # Ask the LLM to analyze the research question
    prompt = f"""
You are a research agent.

Analyze the user's question and provide a clear,
well-structured answer.

Use the following structure:

1. Overview
2. Key Points
3. Detailed Explanation
4. Conclusion

Be accurate and do not make up specific facts.

User Question:
{query}
"""

    answer = ask_llm(prompt)

    return answer