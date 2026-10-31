"""Backs the claims in posts/why-you-cant-just-grep-your-way-to-semantic-search.md.
Run with: uv run examples/why-you-cant-just-grep-your-way-to-semantic-search/vector_search_demo.py

Requires a local Ollama server with nomic-embed-text pulled -- the same
backend used in examples/what-is-an-embedding/embedding_similarity_demo.py.
A "vector database" is this same idea (embed everything, compare by cosine
similarity) at a scale and speed that a plain Python loop doesn't have to
handle; this script does the real comparison, just without the indexing.
"""

import json
import math
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/embed"


def get_embedding(text: str) -> list[float]:
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": "nomic-embed-text", "input": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["embeddings"][0]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


documents = [
    "Our return policy allows refunds within 30 days of purchase.",
    "The espresso machine needs to be descaled every three months.",
    "To reset your password, click the link in the email we sent you.",
]

query = "How do I get my money back on something I bought?"

query_vec = get_embedding(query)
doc_vecs = [get_embedding(doc) for doc in documents]

print(f"query: {query!r}\n")
scores = [(cosine_similarity(query_vec, v), doc) for v, doc in zip(doc_vecs, documents)]
for score, doc in sorted(scores, reverse=True):
    print(f"{score:.4f}  {doc}")
