"""Search the MedlinePlus chunks and build an answer."""

import json
import os
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_DIR = Path("data")
# The only place the embedding model is named, build_index.py uses it too
MODEL_NAME = "all-mpnet-base-v2"
THRESHOLD_PATH = Path("threshold.json")
DISCLAIMER = "General health information from MedlinePlus, not medical advice. Please see a doctor for your own situation."
NOT_FOUND = "I could not find this in the MedlinePlus health topics."


def load_chunks():
    return json.loads((DATA_DIR / "chunks.json").read_text())


def load_embeddings():
    return np.load(DATA_DIR / "embeddings.npy")


def load_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def load_threshold():
    return json.loads(THRESHOLD_PATH.read_text())["threshold"]


def embed_scores(question, model, embeddings):
    # Vectors are normalized, so the dot product is the cosine similarity
    q = model.encode([question], normalize_embeddings=True)[0]
    return embeddings @ q


def build_tfidf(chunks):
    vectorizer = TfidfVectorizer(stop_words="english", sublinear_tf=True)
    matrix = vectorizer.fit_transform([c["text"] for c in chunks])
    return vectorizer, matrix


def tfidf_scores(question, vectorizer, matrix):
    # TF-IDF rows are already L2 normalized, so this is also cosine similarity
    q = vectorizer.transform([question])
    return (matrix @ q.T).toarray().ravel()


def top_topics(scores, chunks, k=3):
    # Best chunk per topic, so the same topic is not listed twice
    results = []
    seen = set()
    for i in np.argsort(-scores):
        title = chunks[i]["title"]
        if title in seen:
            continue
        seen.add(title)
        results.append({"title": title, "url": chunks[i]["url"], "text": chunks[i]["text"], "score": float(scores[i])})
        if len(results) == k:
            break
    return results


def answer(question, model, embeddings, chunks, threshold, k=3):
    results = top_topics(embed_scores(question, model, embeddings), chunks, k)
    found = results[0]["score"] >= threshold
    return {"found": found, "results": results if found else []}


def format_result(r):
    # Markdown line used by the Streamlit app
    return f"**{r['title']}** (similarity {r['score']:.2f}) [source]({r['url']})"


def generate_answer(question, results):
    """Optional: only runs if OPENAI_API_KEY is set. Not part of the measured results."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key or not results:
        return None
    from openai import OpenAI

    passages = "\n\n".join(r["title"] + ": " + r["text"] for r in results)
    prompt = (
        "Answer the question using only the passages below. "
        "If the passages do not contain the answer, reply exactly: not found.\n\n"
        "Passages:\n" + passages + "\n\nQuestion: " + question
    )
    client = OpenAI(api_key=key)
    reply = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return reply.choices[0].message.content
