import speech_recognition as sr


def listen_to_user():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("\n🎤 Listening...")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        audio = recognizer.listen(source)

    try:

        print("🔄 Converting speech to text...")

        text = recognizer.recognize_google(audio)

        print(f"🗣️ You said: {text}")

        return text

    except sr.UnknownValueError:

        print("❌ I could not understand the audio.")
        return None

    except sr.RequestError as e:

        print(f"❌ Speech recognition service error: {e}")
        return None