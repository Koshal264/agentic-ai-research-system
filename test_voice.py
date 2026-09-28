from utils.voice import listen_to_user
from utils.speaker import speak
from agents.supervisor import supervisor_agent


def main():

    print("\n================================")
    print("   SOVEREIGN AI VOICE ASSISTANT")
    print("================================")

    query = listen_to_user()

    if not query:
        print("No voice input received.")
        return

    print("\n🤖 Processing your request...")

    response = supervisor_agent(
        query=query
    )

    print("\n================================")
    print("AI RESPONSE")
    print("================================")

    print(response)

    print("\n🔊 Speaking response...")

    speak(response)


if __name__ == "__main__":
    main()