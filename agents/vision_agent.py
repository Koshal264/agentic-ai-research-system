from utils.llm import ask_vision_llm


def vision_agent(image_path: str, query: str) -> str:

    prompt = f"""
You are a vision analysis agent.

Analyze the provided image and answer the user's question
based on what you can see in the image.

Be accurate and do not invent information.

User Question:
{query}
"""

    answer = ask_vision_llm(
        prompt=prompt,
        image_path=image_path
    )

    return answer