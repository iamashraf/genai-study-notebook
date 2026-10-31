"""Backs the claims in posts/why-a-few-examples-teach-what-instructions-cant.md.
Run with: uv run examples/why-a-few-examples-teach-what-instructions-cant/fewshot_demo.py

Requires a local Ollama server (http://localhost:11434) with llama3.1:8b pulled.
"snorkflux" is a word that cannot appear anywhere in the model's training data --
it was made up for this script -- so there is no way to get its meaning right
except from what's shown in the prompt itself.
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


zero_shot_prompt = 'Use the word "snorkflux" in a sentence.'

few_shot_prompt = (
    'A "whatpu" is a small, furry animal native to Tanzania. An example of a '
    "sentence that uses the word whatpu is: We were traveling in Africa and we "
    "saw these very cute whatpus.\n\n"
    'To "farduddle" means to jump up and down really fast. An example of a '
    "sentence that uses the word farduddle is: When the kids heard the ice "
    "cream truck, they started to farduddle with excitement.\n\n"
    'A "snorkflux" is a small device that measures how much it rained '
    "overnight. An example of a sentence that uses the word snorkflux is:"
)

print("--- zero-shot (0 examples) ---")
print(generate(zero_shot_prompt))
print()
print("--- few-shot (2 examples) ---")
print(generate(few_shot_prompt))
