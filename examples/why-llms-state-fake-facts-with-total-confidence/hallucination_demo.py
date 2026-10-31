"""Backs the claims in posts/why-llms-state-fake-facts-with-total-confidence.md.
Run with: uv run examples/why-llms-state-fake-facts-with-total-confidence/hallucination_demo.py

Requires a local Ollama server (http://localhost:11434) with phi3:mini pulled.
"Dr. Elowen Marsh" and "quantum lighthouse theory" are invented for this
script -- neither exists -- so any specific detail the model states about
them cannot have come from a real fact.
"""

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate(prompt: str) -> str:
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": "phi3:mini", "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["response"].strip()


prompt = (
    "What year did Dr. Elowen Marsh publish her famous paper on quantum "
    "lighthouse theory, and which journal was it in? Answer in one or two "
    "sentences."
)

print(generate(prompt))
