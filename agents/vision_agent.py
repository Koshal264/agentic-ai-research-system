from pathlib import Path

from utils.llm import ask_vision_llm


def vision_agent(
    image_path: str,
    query: str
) -> str:
    """
    Vision Agent:
    Analyzes an uploaded image using the vision-capable LLM.
    """

    print("========================================")
    print("VISION AGENT STARTED")
    print("Image:", image_path)
    print("Query:", query)
    print("========================================")

    # Check whether image exists
    image_file = Path(image_path)

    if not image_file.exists():
        return (
            f"Error: Image file not found: {image_path}"
        )

    if not image_file.is_file():
        return (
            f"Error: Invalid image path: {image_path}"
        )

    # Prompt for vision model
    prompt = f"""
You are a helpful Vision AI Agent.

Analyze the uploaded image carefully and answer
the user's question.

Instructions:
1. Describe only what can be observed in the image.
2. Do not invent details.
3. If something is unclear, say that it is unclear.
4. Answer the user's question directly.
5. Be respectful and neutral.
6. Do not make unsupported assumptions about people.

User Question:
{query}
"""

    try:
        answer = ask_vision_llm(
            prompt=prompt,
            image_path=str(image_file)
        )

        return answer

    except Exception as error:
        print("VISION AGENT ERROR:", error)

        return (
            "An error occurred while analyzing the image: "
            f"{str(error)}"
        )