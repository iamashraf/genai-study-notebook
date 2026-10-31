"""Backs the claims in posts/why-chunking-strategy-matters-more-than-your-database.md.
Run with: uv run examples/why-chunking-strategy-matters-more-than-your-database/chunking_demo.py

Requires a local Ollama server with nomic-embed-text pulled.
Same source text, chunked two ways, then queried against the same question
with real embeddings and real cosine similarity.
"""

import json
import math
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/embed"

TEXT = (
    "The project's vector database is Chroma, and the engineer who "
    "configured it, Ashraf, chose it for local-first simplicity over "
    "Pinecone's managed cost."
)

QUERY = "Who configured the vector database?"


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


def chunk(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    chunks = []
    step = size - overlap
    for start in range(0, len(words), step):
        chunk_words = words[start : start + size]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if start + size >= len(words):
            break
    return chunks


def score_all(chunks: list[str], query_vec: list[float]) -> list[tuple[float, str]]:
    scored = [(cosine_similarity(query_vec, get_embedding(c)), c) for c in chunks]
    return sorted(scored, reverse=True)


query_vec = get_embedding(QUERY)

no_overlap = chunk(TEXT, size=10, overlap=0)
with_overlap = chunk(TEXT, size=10, overlap=5)

print("--- chunk size 10, no overlap ---")
for score, c in score_all(no_overlap, query_vec):
    print(f"  {score:.4f}  {c!r}  (has 'Ashraf': {'Ashraf' in c})")
print()

print("--- chunk size 10, overlap 5 ---")
for score, c in score_all(with_overlap, query_vec):
    print(f"  {score:.4f}  {c!r}  (has 'Ashraf': {'Ashraf' in c})")
