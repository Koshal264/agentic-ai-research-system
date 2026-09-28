import subprocess


def speak(text: str):

    if not text:
        return

    subprocess.run(
        ["say", text],
        check=False
    )