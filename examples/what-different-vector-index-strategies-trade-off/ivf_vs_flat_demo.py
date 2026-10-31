"""Backs the claims in posts/what-different-vector-index-strategies-trade-off.md.
Run with: uv run examples/what-different-vector-index-strategies-trade-off/ivf_vs_flat_demo.py

Requires a local Ollama server with nomic-embed-text pulled -- same backend as
examples/why-you-cant-just-grep-your-way-to-semantic-search/vector_search_demo.py.

Flat search compares the query against every stored vector. An IVF-style
index first clusters the vectors (k-means), then at query time only compares
against the vectors inside the nearest cluster(s) -- this script builds both,
for real, on the same documents, and counts how many vectors each one
actually has to visit.
"""

import json
import math
import random
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/embed"

documents = [
    "Our return policy allows refunds within 30 days of purchase.",
    "You can send back an unopened item for a full refund within a month.",
    "Exchanges and refunds are processed at any store location.",
    "The espresso machine needs to be descaled every three months.",
    "Grind your coffee beans fresh for the best espresso crema.",
    "Our shop roasts a new batch of coffee beans every Tuesday.",
    "To reset your password, click the link in the email we sent you.",
    "Two-factor authentication can be enabled from your account settings.",
    "If you're locked out of your account, contact support to verify your identity.",
]

query = "How do I get my money back on something I bought?"


def get_embedding(text: str) -> list[float]:
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": "nomic-embed-text", "input": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["embeddings"][0]


def normalize(v: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def kmeans(vectors: list[list[float]], k: int, iterations: int = 10) -> list[int]:
    random.seed(0)
    centroids = random.sample(vectors, k)
    assignments = [0] * len(vectors)
    for _ in range(iterations):
        for i, v in enumerate(vectors):
            assignments[i] = max(range(k), key=lambda c: cosine_similarity(v, centroids[c]))
        for c in range(k):
            members = [v for i, v in enumerate(vectors) if assignments[i] == c]
            if members:
                mean = [sum(dim) / len(members) for dim in zip(*members)]
                centroids[c] = normalize(mean)
    return assignments, centroids


vectors = [normalize(get_embedding(doc)) for doc in documents]
query_vec = normalize(get_embedding(query))

# Flat: visit every single vector.
flat_scores = sorted(
    ((cosine_similarity(query_vec, v), doc) for v, doc in zip(vectors, documents)),
    reverse=True,
)

# IVF-style: cluster the vectors first, then only search the nearest cluster.
k = 3
assignments, centroids = kmeans(vectors, k)
nearest_cluster = max(range(k), key=lambda c: cosine_similarity(query_vec, centroids[c]))
cluster_docs = [
    (v, doc) for v, doc, a in zip(vectors, documents, assignments) if a == nearest_cluster
]
ivf_scores = sorted(
    ((cosine_similarity(query_vec, v), doc) for v, doc in cluster_docs), reverse=True
)

print(f"query: {query!r}\n")

print(f"FLAT search -- visited all {len(documents)} vectors:")
for score, doc in flat_scores[:3]:
    print(f"  {score:.4f}  {doc}")

print(f"\nIVF-style search -- visited only {len(cluster_docs)} vectors (nearest cluster):")
for score, doc in ivf_scores[:3]:
    print(f"  {score:.4f}  {doc}")

print(f"\ntop match same for both: {flat_scores[0][1] == ivf_scores[0][1]}")
