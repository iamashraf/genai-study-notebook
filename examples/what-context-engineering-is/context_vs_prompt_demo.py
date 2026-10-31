"""Backs the claims in posts/what-context-engineering-is.md.
Run with: uv run examples/what-context-engineering-is/context_vs_prompt_demo.py

Requires a local Ollama server (http://localhost:11434) with llama3.1:8b pulled.

Asks the exact same well-crafted prompt twice, about a fictional company
policy that cannot exist in the model's training data (made up for this
script). The first call has no relevant context -- just the prompt, however
carefully worded. The second call is byte-for-byte the same prompt, with one
short real snippet of policy text injected ahead of it. This isolates the
variable: wording is held constant, only the surrounding context changes.
"""

import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

# A well-crafted prompt by prompt-engineering standards: clear role, clear
# question, explicit output format. None of that helps if the model has
# never seen the fact it's being asked about.
WELL_CRAFTED_PROMPT = (
    "You are a precise HR assistant. Answer in exactly one sentence, "
    "stating the number directly. Question: Under Nimbusware's remote "
    "work policy, how many co-working-space reimbursement days is an "
    "engineer allowed per month?"
)

# A short, real snippet of the (invented) policy -- the kind of thing a
# retrieval step or a system prompt would inject. Nimbusware is not a real
# company; this policy text exists only in this script.
POLICY_SNIPPET = (
    "Nimbusware Remote Work Policy, Section 4.2: Engineers working "
    "remotely may claim reimbursement for up to 6 co-working-space days "
    "per calendar month. Days beyond 6 require manager approval."
)


def generate(prompt: str) -> str:
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({"model": "llama3.1:8b", "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["response"].strip()


print("--- prompt only, no relevant context ---")
print(generate(WELL_CRAFTED_PROMPT))
print()

with_context_prompt = f"Context:\n{POLICY_SNIPPET}\n\n{WELL_CRAFTED_PROMPT}"
print("--- identical prompt, with policy snippet injected as context ---")
print(generate(with_context_prompt))
