"""Backs the claims in posts/what-different-ways-to-chunk-a-document-exist.md.
Run with: uv run examples/what-different-ways-to-chunk-a-document-exist/semantic_chunking_demo.py

Requires a local Ollama server with nomic-embed-text pulled -- same backend as
examples/why-you-cant-just-grep-your-way-to-semantic-search/vector_search_demo.py.

Fixed-size chunking (here: every 2 sentences) doesn't know where one topic
ends and another begins. Semantic chunking finds that boundary for real, by
embedding each sentence and looking for the point where similarity between
consecutive sentences drops the most.
"""

import json
import math
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/embed"

sentences = [
    "Our espresso machine needs to be descaled every three months.",
    "Fresh coffee beans make a noticeably better shot.",
    "The milk steamer should be cleaned after every use.",
    "To reset your password, click the link we emailed you.",
    "Two-factor authentication can be enabled in account settings.",
    "If you're locked out, contact support to verify your identity.",
]


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


vectors = [get_embedding(s) for s in sentences]

print("consecutive-sentence similarity:")
gaps = []
for i in range(len(sentences) - 1):
    sim = cosine_similarity(vectors[i], vectors[i + 1])
    gaps.append(sim)
    print(f"  [{i}]-[{i+1}]  {sim:.4f}")

boundary = gaps.index(min(gaps))
print(f"\nbiggest similarity drop is between sentence [{boundary}] and [{boundary+1}]")
print(f"  [{boundary}] {sentences[boundary]!r}")
print(f"  [{boundary+1}] {sentences[boundary+1]!r}")

print("\nfixed-size chunking (2 sentences per chunk):")
for i in range(0, len(sentences), 2):
    print(f"  chunk: {sentences[i:i+2]}")

print("\nsemantic chunking (split at the similarity drop):")
print(f"  chunk: {sentences[:boundary+1]}")
print(f"  chunk: {sentences[boundary+1:]}")
