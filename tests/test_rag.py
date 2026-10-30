import pytest

import build_index
import rag


@pytest.fixture(scope="module")
def index():
    return rag.load_chunks(), rag.load_embeddings(), rag.load_model(), rag.load_threshold()


def test_clean_html_makes_lines():
    lines = build_index.clean_html("<p>Hello &amp; welcome</p><ul><li>one</li><li>two</li></ul>")
    assert lines == ["Hello & welcome", "one", "two"]


def test_chunks_have_title_and_stay_short():
    lines = ["word " * 70, "word " * 70, "short line"]
    chunks = build_index.split_into_chunks("Flu", lines)
    assert len(chunks) == 2
    assert all(c.startswith("Flu. ") for c in chunks)


def test_index_matches_chunks(index):
    chunks, embeddings, model, threshold = index
    assert len(chunks) == embeddings.shape[0]
    assert all(c["url"].startswith("https://medlineplus.gov/") for c in chunks)


@pytest.mark.parametrize(
    "question, topic",
    [("my child has itchy red spots and a fever", "Chickenpox"), ("how can I quit cigarettes", "Quitting Smoking")],
)
def test_finds_expected_topic(index, question, topic):
    chunks, embeddings, model, threshold = index
    result = rag.answer(question, model, embeddings, chunks, threshold)
    assert result["found"]
    assert topic in [r["title"] for r in result["results"]]


def test_non_medical_question_not_found(index):
    chunks, embeddings, model, threshold = index
    result = rag.answer("what is the price of bitcoin today", model, embeddings, chunks, threshold)
    assert not result["found"]
    assert result["results"] == []


def test_no_key_means_no_generation(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert rag.generate_answer("anything", [{"title": "Flu", "text": "x"}]) is None


def test_format_result_shows_title_score_and_link():
    r = {"title": "Flu", "url": "https://medlineplus.gov/flu.html", "score": 0.71234}
    text = rag.format_result(r)
    assert "**Flu**" in text and "0.71" in text and "(https://medlineplus.gov/flu.html)" in text
