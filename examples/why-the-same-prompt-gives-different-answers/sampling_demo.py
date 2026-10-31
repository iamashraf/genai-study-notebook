"""Backs the claims in posts/why-the-same-prompt-gives-different-answers.md.
Run with: uv run examples/why-the-same-prompt-gives-different-answers/sampling_demo.py

Requires a local Ollama server (http://localhost:11434) with llama3.1:8b pulled.
Same prompt, called twice at temperature=0 and twice at temperature=1.
"""

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"


def generate(prompt: str, temperature: float) -> str:
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(
            {
                "model": "llama3.1:8b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            }
        ).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["response"].strip()


prompt = "Write one sentence about the ocean."

print("--- temperature = 0 (two calls) ---")
print(generate(prompt, 0))
print(generate(prompt, 0))
print()
print("--- temperature = 1 (two calls) ---")
print(generate(prompt, 1))
print(generate(prompt, 1))
