"""Optional speech to text with faster-whisper. Runs on your own machine."""

import io

from faster_whisper import WhisperModel

MODEL_NAME = "base.en"
_model = None


def transcribe(audio_bytes):
    global _model
    # Load the model the first time only, it is downloaded once and then cached
    if _model is None:
        _model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")
    segments, info = _model.transcribe(io.BytesIO(audio_bytes), language="en")
    return " ".join(s.text.strip() for s in segments).strip()
