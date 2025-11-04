"""Voice I/O stubs for addvar.

These are minimal helpers. Replace or extend with real audio capture and ASR/voice model integration.
"""

try:
    import pyttsx3
except Exception:
    pyttsx3 = None


def speak(text: str):
    """Speak text via pyttsx3 if available."""
    if pyttsx3 is None:
        raise RuntimeError("pyttsx3 not installed")
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def record_placeholder(duration: float = 3.0):
    """Placeholder for audio recording. Implement using sounddevice or other library."""
    raise NotImplementedError("Audio recording is a placeholder. Install `sounddevice` and implement capture.")
