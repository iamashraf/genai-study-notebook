"""Backs the claims in posts/what-problem-does-rag-actually-solve.md.
Run with: uv run examples/what-problem-does-rag-actually-solve/rag_demo.py

Requires my local AskTheDocs RAG build running (http://localhost:8000),
with its seed_sources.yaml already loaded -- this script asks it a real
question and shows the actual retrieved citations that grounded the answer.
"""

import json
import urllib.request

RAG_URL = "http://localhost:8000/v1/ask"


def ask(query: str, k: int = 5) -> dict:
    req = urllib.request.Request(
        RAG_URL,
        data=json.dumps({"query": query, "k": k}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


result = ask("What problem does retrieval-augmented generation solve for language models?")

print("answer:")
print(result["answer"])
print()
print("citations (the actual documents retrieved to ground that answer):")
for c in result["citations"]:
    print(f"  {c}")
