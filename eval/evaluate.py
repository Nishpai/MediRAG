"""Measure retrieval on the hand-written questions and pick the not-found threshold.

Run from the repo root: python eval/evaluate.py
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import rag  # noqa: E402


def load_questions():
    with open("eval/questions.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rank_of(expected, results):
    # 1 based rank of the expected topic, or 0 if it is not in the list
    for i, r in enumerate(results):
        if r["title"] == expected:
            return i + 1
    return 0


def metrics(ranks):
    ranks = np.array(ranks)
    hit1 = np.mean(ranks == 1)
    hit3 = np.mean((ranks >= 1) & (ranks <= 3))
    mrr = np.mean([1 / r if r > 0 else 0 for r in ranks])
    return round(float(hit1), 3), round(float(hit3), 3), round(float(mrr), 3)


def pick_threshold(in_scores, out_scores):
    # Try the midpoint between each pair of neighbouring dev scores as a cut
    # and keep the one that gets the most dev questions right
    scores = sorted(in_scores + out_scores)
    best_t, best_correct = 0.0, -1
    for a, b in zip(scores, scores[1:]):
        t = (a + b) / 2
        correct = sum(s >= t for s in in_scores) + sum(s < t for s in out_scores)
        if correct > best_correct:
            best_t, best_correct = t, correct
    return round(best_t, 3)


def main():
    questions = load_questions()
    chunks = rag.load_chunks()
    embeddings = rag.load_embeddings()
    model = rag.load_model()
    vectorizer, matrix = rag.build_tfidf(chunks)

    rows = []
    for q in questions:
        emb = rag.top_topics(rag.embed_scores(q["question"], model, embeddings), chunks, k=10)
        tfi = rag.top_topics(rag.tfidf_scores(q["question"], vectorizer, matrix), chunks, k=10)
        rows.append({**q, "emb": emb, "tfidf": tfi})

    dev = [r for r in rows if r["split"] == "dev"]
    test = [r for r in rows if r["split"] == "test"]

    dev_in = [r["emb"][0]["score"] for r in dev if r["expected_topic"] != "OUT"]
    dev_out = [r["emb"][0]["score"] for r in dev if r["expected_topic"] == "OUT"]
    threshold = pick_threshold(dev_in, dev_out)
    Path("threshold.json").write_text(json.dumps({"threshold": threshold}) + "\n")

    test_in = [r for r in test if r["expected_topic"] != "OUT"]
    test_out = [r for r in test if r["expected_topic"] == "OUT"]
    results = {"threshold": threshold, "test_in_scope": len(test_in), "test_out_of_scope": len(test_out)}
    for method in ["emb", "tfidf"]:
        ranks = [rank_of(r["expected_topic"], r[method]) for r in test_in]
        results[method] = dict(zip(["hit@1", "hit@3", "mrr"], metrics(ranks)))

    rejected = sum(r["emb"][0]["score"] < threshold for r in test_out)
    wrongly_rejected = sum(r["emb"][0]["score"] < threshold for r in test_in)
    results["out_of_scope_rejected"] = rejected
    results["in_scope_wrongly_rejected"] = wrongly_rejected
    results["dev_in_scope_top_scores"] = [round(s, 3) for s in sorted(dev_in)]
    results["dev_out_of_scope_top_scores"] = [round(s, 3) for s in sorted(dev_out)]
    print(json.dumps(results, indent=2))

    print("\nEmbedding misses at top 1 (test):")
    for r in test_in:
        if r["emb"][0]["title"] != r["expected_topic"]:
            got = [x["title"] for x in r["emb"][:3]]
            print("-", r["question"], "| expected:", r["expected_topic"], "| got:", got)

    print("\nOut-of-scope top scores (test):")
    for r in test_out:
        print("-", r["question"], round(r["emb"][0]["score"], 3), r["emb"][0]["title"])

    Path("eval/results.json").write_text(json.dumps(results, indent=2) + "\n")
    save_chart(results, [r["emb"][0]["score"] for r in test_in], [r["emb"][0]["score"] for r in test_out])


def save_chart(results, in_scores, out_scores):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    names = ["hit@1", "hit@3", "mrr"]
    x = np.arange(len(names))
    ax1.bar(x - 0.2, [results["emb"][n] for n in names], 0.4, label="embeddings")
    ax1.bar(x + 0.2, [results["tfidf"][n] for n in names], 0.4, label="TF-IDF")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names)
    ax1.set_ylim(0, 1)
    ax1.set_title("Retrieval on test questions")
    ax1.legend()
    ax2.hist(in_scores, bins=10, alpha=0.6, label="medical questions")
    ax2.hist(out_scores, bins=10, alpha=0.6, label="out of scope")
    ax2.axvline(results["threshold"], color="black", linestyle="--", label="threshold")
    ax2.set_xlabel("best cosine similarity")
    ax2.set_title("Top score, test questions")
    ax2.legend()
    fig.tight_layout()
    fig.savefig("images/results.png", dpi=120)


if __name__ == "__main__":
    main()
