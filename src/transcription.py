from src.speech_to_text import speech_to_text


def transcribe_audio(audio_path):
    """
    Convert an audio file into text.
    """

    transcript = speech_to_text(audio_path)

    return {
        "success": True,
        "text": transcript
    }