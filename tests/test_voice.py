from pathlib import Path

import pytest

pytest.importorskip("faster_whisper")

import rag  # noqa: E402
import voice  # noqa: E402

CLIP = Path(__file__).parent / "audio" / "question.wav"


def test_transcribe_clip_and_search():
    # The clip was made with espeak-ng saying "I have a painful red swollen big toe at night"
    text = voice.transcribe(CLIP.read_bytes())
    assert "toe" in text.lower()
    result = rag.answer(text, rag.load_model(), rag.load_embeddings(), rag.load_chunks(), rag.load_threshold())
    assert "Gout" in [r["title"] for r in result["results"]]
