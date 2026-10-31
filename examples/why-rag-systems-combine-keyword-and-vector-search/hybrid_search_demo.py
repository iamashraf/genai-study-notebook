"""Backs the claims in posts/why-rag-systems-combine-keyword-and-vector-search.md.
Run with: uv run examples/why-rag-systems-combine-keyword-and-vector-search/hybrid_search_demo.py

A real (small) BM25 implementation -- the classic keyword-ranking algorithm --
and real vector cosine similarity (via the same local Ollama embedding model
used in examples/what-is-an-embedding), run against the same three documents
and two queries, so the two search methods can be compared head to head.
"""

import json
import math
import urllib.request
from collections import Counter

OLLAMA_URL = "http://localhost:11434/api/embed"

DOCUMENTS = [
    "The replacement filter for model QX-4471 ships within two business days.",
    "Our most popular espresso machine has a sleek stainless steel design.",
    "Return any product within 30 days for a full refund, no questions asked.",
]

K1, B = 1.5, 0.75


def tokenize(text: str) -> list[str]:
    return text.lower().replace(",", "").replace(".", "").split()


tokenized_docs = [tokenize(d) for d in DOCUMENTS]
doc_count = len(DOCUMENTS)
avg_doc_len = sum(len(d) for d in tokenized_docs) / doc_count
doc_freq: Counter = Counter()
for doc in tokenized_docs:
    for term in set(doc):
        doc_freq[term] += 1


def bm25_score(query: str, doc_tokens: list[str]) -> float:
    term_freq = Counter(doc_tokens)
    score = 0.0
    for term in tokenize(query):
        if term not in term_freq:
            continue
        idf = math.log((doc_count - doc_freq[term] + 0.5) / (doc_freq[term] + 0.5) + 1)
        tf = term_freq[term]
        denom = tf + K1 * (1 - B + B * len(doc_tokens) / avg_doc_len)
        score += idf * (tf * (K1 + 1)) / denom
    return score


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


for query in ["QX-4471", "How do I get my money back on something I bought?"]:
    print(f"=== query: {query!r} ===")
    print("BM25 (keyword):")
    for doc, tokens in zip(DOCUMENTS, tokenized_docs):
        print(f"  {bm25_score(query, tokens):.4f}  {doc}")
    print("vector cosine similarity (meaning):")
    query_vec = get_embedding(query)
    for doc in DOCUMENTS:
        print(f"  {cosine_similarity(query_vec, get_embedding(doc)):.4f}  {doc}")
    print()
