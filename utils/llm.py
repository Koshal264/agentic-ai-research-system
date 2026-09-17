import base64
import mimetypes

from openai import OpenAI


# =========================================================
# OLLAMA CLIENT
# =========================================================

client = OpenAI(
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama"
)


# =========================================================
# NORMAL TEXT LLM
# =========================================================

def ask_llm(prompt: str) -> str:

    response = client.chat.completions.create(
        model="gemma2:2b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


# =========================================================
# VISION LLM
# =========================================================

def ask_vision_llm(
    prompt: str,
    image_path: str
) -> str:

    print("========================================")
    print("VISION LLM")
    print("Image:", image_path)
    print("========================================")

    # Read image
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    # Convert image to Base64
    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    # Detect actual image type
    mime_type, _ = mimetypes.guess_type(
        image_path
    )

    if mime_type is None:
        mime_type = "image/jpeg"

    print("MIME type:", mime_type)

    # Create image data URL
    image_url = (
        f"data:{mime_type};base64,"
        f"{image_base64}"
    )

    # Send image to Gemma Vision
    response = client.chat.completions.create(
        model="gemma3:4b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content