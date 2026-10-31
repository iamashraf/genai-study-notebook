"""Backs the claims in posts/what-is-an-embedding.md.
Run with: uv run examples/what-is-an-embedding/embedding_similarity_demo.py

Requires a local Ollama server with the nomic-embed-text model pulled
(http://localhost:11434, `ollama pull nomic-embed-text`) -- this is the
embeddings backend already running for the AskTheDocs RAG build.
These are real embedding vectors, not hand-picked illustrative numbers.
"""

import math
import urllib.request
import json

OLLAMA_URL = "http://localhost:11434/api/embed"


def get_embedding(word: str) -> list[float]:
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": "nomic-embed-text", "input": word}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["embeddings"][0]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


words = ["cat", "kitten", "car"]
vectors = {w: get_embedding(w) for w in words}

print(f"embedding dimensions: {len(vectors['cat'])}")
print(f"similarity(cat, kitten) = {cosine_similarity(vectors['cat'], vectors['kitten']):.4f}")
print(f"similarity(cat, car)    = {cosine_similarity(vectors['cat'], vectors['car']):.4f}")
