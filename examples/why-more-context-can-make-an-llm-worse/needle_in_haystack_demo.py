"""Backs the claims in posts/why-more-context-can-make-an-llm-worse.md.
Run with: uv run examples/why-more-context-can-make-an-llm-worse/needle_in_haystack_demo.py

Requires a local Ollama server (http://localhost:11434) with llama3.1:8b pulled.

A "needle in a haystack" test: one specific, checkable fact (a made-up
vault code) is buried inside a block of filler sentences, and the model is
asked to recall it. We vary three things the "lost in the middle" / context
rot literature points at: how much surrounding material there is, where
the fact sits in it (start/middle/end), and how many other fact-shaped
decoys (fake codes for other rooms) compete with it. num_ctx is set well
above every prompt's actual token count so a result can't be confused with
simply running out of context window -- that's a different, separate
failure covered in posts/what-a-context-window-actually-limits.md.

Each trial reshuffles the filler/decoys with a different random seed, so
repeated trials aren't just the same cached prompt sampled again.
"""

import json
import random
import time
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"
SECRET_SENTENCE = "The secret access code for the vault is XQ-7491."
CODE = "XQ-7491"
TRIALS = 5

BASE_FILLER = [
    "The city of Lisbon sits on seven hills along the Tagus river.",
    "Honey never spoils if it is stored in a sealed container.",
    "A standard soccer match lasts ninety minutes plus stoppage time.",
    "The Sahara desert expands and contracts with the seasons.",
    "Octopuses have three hearts and blue-tinted blood.",
]

ROOMS = [
    "west wing archive", "maintenance door", "old server room", "visitor parking gate",
    "backup generator panel", "loading dock", "east stairwell", "rooftop access hatch",
    "records storage cage", "north fire exit", "executive elevator", "mailroom cabinet",
    "janitorial closet", "server rack 4", "server rack 9", "break room vending machine",
    "bike storage room", "security office", "IT supply closet", "print room",
    "conference room B", "conference room C", "basement utility room", "loading ramp",
    "south emergency exit", "data center cage 2", "data center cage 3", "lab freezer",
    "chemical storage locker", "roof HVAC unit",
]
LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"


def make_decoy_codes(n):
    out = []
    for i in range(n):
        room = ROOMS[i % len(ROOMS)]
        code = f"{LETTERS[i % len(LETTERS)]}{LETTERS[(i * 3) % len(LETTERS)]}-{1000 + (i * 37) % 8999}"
        out.append(f"The access code for the {room} is {code}.")
    return out


def make_filler(n):
    return [f"{BASE_FILLER[i % len(BASE_FILLER)]} (note {i})" for i in range(n)]


def generate(prompt, temperature=0.7, num_ctx=32768):
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_ctx": num_ctx},
        }).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.load(resp)
        return data["response"].strip(), data.get("prompt_eval_count")


QUESTION = (
    "Question: what string of letters and numbers would let you open the vault? "
    "Reply with only that string, nothing else."
)


def build_prompt(n_filler, n_decoys, position, seed):
    body = make_filler(n_filler) + make_decoy_codes(n_decoys)
    random.Random(seed).shuffle(body)
    if position == "start":
        lines = [SECRET_SENTENCE] + body
    elif position == "end":
        lines = body + [SECRET_SENTENCE]
    else:
        half = len(body) // 2
        lines = body[:half] + [SECRET_SENTENCE] + body[half:]
    return " ".join(lines) + f"\n\n{QUESTION}"


CONDITIONS = [
    ("short, no decoys, middle", 10, 0, "middle"),
    ("long (~3.6k tok), 6 decoys, start", 200, 6, "start"),
    ("long (~3.6k tok), 6 decoys, middle", 200, 6, "middle"),
    ("long (~3.6k tok), 6 decoys, end", 200, 6, "end"),
    ("long (~3.1k tok), 30 competing decoys, middle", 150, 30, "middle"),
]

if __name__ == "__main__":
    for label, n_filler, n_decoys, position in CONDITIONS:
        print(f"--- {label} ---")
        hits = 0
        tok_counts = []
        for i in range(TRIALS):
            prompt = build_prompt(n_filler, n_decoys, position, seed=i)
            t0 = time.time()
            out, ptoks = generate(prompt)
            dt = time.time() - t0
            correct = CODE in out
            hits += correct
            if ptoks:
                tok_counts.append(ptoks)
            print(f"  trial {i}: correct={correct} prompt_tokens={ptoks} time={dt:.1f}s output={out!r}")
        avg_tok = round(sum(tok_counts) / len(tok_counts)) if tok_counts else None
        print(f"  accuracy: {hits}/{TRIALS}  avg_prompt_tokens={avg_tok}")
