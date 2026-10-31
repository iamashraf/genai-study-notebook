"""Backs the claims in posts/what-thinking-step-by-step-actually-changes.md.
Run with: uv run examples/what-thinking-step-by-step-actually-changes/cot_demo.py

Requires a local Ollama server (http://localhost:11434) with llama3.1:8b pulled.
Same two-step word problem, asked two different ways.
"""

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate(prompt: str) -> str:
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": "llama3.1:8b", "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["response"].strip()


question = (
    "A juggler has 24 balls. Half are golf balls, and half of the golf balls "
    "are blue. How many blue golf balls are there?"
)

direct_prompt = f"Answer with only the final number, no explanation. {question}"
cot_prompt = f"{question} Let's think step by step."

print("--- direct answer ---")
print(generate(direct_prompt))
print()
print("--- chain-of-thought ---")
print(generate(cot_prompt))
