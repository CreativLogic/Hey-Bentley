"""
Bentley Voice — Speech I/O
Handles microphone listening and text-to-speech output.
"""
import pyttsx3
import speech_recognition as sr
from config import VOICE_RATE, VOICE_VOLUME, BENTLEY_NAME
from rich.console import Console

console = Console()
engine  = pyttsx3.init()
engine.setProperty("rate",   VOICE_RATE)
engine.setProperty("volume", VOICE_VOLUME)

# Pick a decent voice if available
voices = engine.getProperty("voices")
for v in voices:
    if "david" in v.name.lower() or "mark" in v.name.lower():
        engine.setProperty("voice", v.id)
        break

recognizer = sr.Recognizer()


def speak(text: str):
    console.print(f"[bold cyan]{BENTLEY_NAME}:[/bold cyan] {text}")
    engine.say(text)
    engine.runAndWait()


def listen(timeout: int = 8, phrase_time_limit: int = 12) -> str:
    """Capture one phrase from the microphone. Returns lowercase text or ''."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        console.print("[dim]Listening...[/dim]")
        try:
            audio = recognizer.listen(source, timeout=timeout,
                                       phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio).lower().strip()
        console.print(f"[bold yellow]You:[/bold yellow] {text}")
        return text
    except sr.UnknownValueError:
        speak("I didn't catch that — could you repeat?")
        return ""
    except sr.RequestError:
        speak("My speech service is unavailable right now.")
        return ""


def confirm(prompt: str) -> bool:
    """Ask Bentley to verbally confirm an action. Returns True if user says yes."""
    speak(f"{prompt} — should I go ahead?")
    response = listen(timeout=6)
    return any(w in response for w in ["yes", "yeah", "sure", "go ahead",
                                        "do it", "confirm", "yep", "ok"])
