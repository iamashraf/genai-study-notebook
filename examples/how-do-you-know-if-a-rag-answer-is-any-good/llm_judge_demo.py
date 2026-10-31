"""Backs the claims in posts/how-do-you-know-if-a-rag-answer-is-any-good.md.
Run with: uv run examples/how-do-you-know-if-a-rag-answer-is-any-good/llm_judge_demo.py

Requires a local Ollama server with llama3.1:8b pulled.
Two candidate answers to the same question, graded by a second LLM call
for faithfulness to the given context -- one is accurate, one contradicts
the context on purpose, to see whether the judge actually catches it.
"""

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

CONTEXT = "Our return policy allows refunds within 30 days of purchase, no questions asked."

CANDIDATES = {
    "faithful": "You can return the item within 30 days of purchase for a refund.",
    "unfaithful (90 days + free shipping, neither is in the context)": (
        "You can return the item within 90 days of purchase for a refund, "
        "plus we will cover return shipping."
    ),
}


def judge(context: str, answer: str) -> str:
    prompt = (
        f"Context: {context}\n\n"
        f"Answer to evaluate: {answer}\n\n"
        "Rate the answer's faithfulness to the context on a scale of 1-5, "
        "where 5 means fully supported by the context and 1 means it "
        "contradicts the context. Respond with just the number, then a "
        "one-sentence reason."
    )
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": "llama3.1:8b", "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["response"].strip()


for label, answer in CANDIDATES.items():
    print(f"--- candidate: {label} ---")
    print(f"answer: {answer}")
    print(f"judge:  {judge(CONTEXT, answer)}")
    print()
