"""Ask one question from the command line.

Example: python ask.py "what helps with a migraine"
"""

import sys

import rag


def main():
    question = " ".join(sys.argv[1:]) or input("Question: ")
    chunks = rag.load_chunks()
    embeddings = rag.load_embeddings()
    model = rag.load_model()
    result = rag.answer(question, model, embeddings, chunks, rag.load_threshold())

    print(rag.DISCLAIMER)
    print()
    if not result["found"]:
        print(rag.NOT_FOUND)
        return
    for r in result["results"]:
        print(f"[{r['score']:.2f}] {r['title']} ({r['url']})")
        print(r["text"])
        print()
    generated = rag.generate_answer(question, result["results"])
    if generated:
        print("Generated answer (optional, not evaluated):", generated)


if __name__ == "__main__":
    main()
