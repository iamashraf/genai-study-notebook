"""Semantic memory demo: durable facts, not a transcript.

Session 1: the user mentions a few stable facts about themselves in passing.
The agent extracts them as "key: value" pairs -- not a dated event, not the
chat log -- into a small JSON store.

Session 2: a brand-new conversation. No transcript from session 1 is
available or used. Only the fact store is loaded, and the agent answers a
question with it. The point: the fact is usable with no episodic trace of
when or how it was learned.
"""
import json, os, tempfile, urllib.request

OLLAMA = "http://localhost:11434"
MODEL = "llama3.1:8b"
STORE = os.path.join(tempfile.gettempdir(), "semantic_memory_demo.json")


def chat(prompt):
    req = urllib.request.Request(
        OLLAMA + "/api/chat",
        json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0},
        }).encode(),
        {"Content-Type": "application/json"},
    )
    r = json.load(urllib.request.urlopen(req, timeout=300))
    return r["message"]["content"].strip()


# ---- Session 1: durable facts come up in passing ----
session1 = [
    "Hey, I'm Marco. Just so you know, I'm vegetarian.",
    "I'm based in Toronto, work remote.",
    "I'm a backend engineer, mostly Go and Postgres.",
]
print("=== SESSION 1 (user messages) ===")
for m in session1:
    print(" -", m)

transcript = "\n".join(session1)
extracted = chat(
    "Read this chat. Pull out each durable fact about the user as a "
    "'key: value' line -- a stable attribute like diet, home city, or job, "
    "not an event or a date. One fact per line, lowercase keys, no bullets, "
    "nothing else.\n\n" + transcript
)
facts = {}
for line in extracted.splitlines():
    line = line.strip().lstrip("-• ").strip()
    if ":" in line:
        k, v = line.split(":", 1)
        facts[k.strip().lower()] = v.strip()

print("\n=== FACTS WRITTEN TO THE SEMANTIC MEMORY STORE ===")
for k, v in facts.items():
    print(f" - {k}: {v}")
json.dump(facts, open(STORE, "w"), indent=2)
# Session 1 ends. Its transcript is gone -- only the key:value file remains.
# There is no record of "when" or "how" these facts were said.

# ---- Session 2: a new conversation, no transcript carried over ----
question = "I'm about to book Marco a lunch meeting. What should the restaurant avoid, and where is he based?"
print("\n=== SESSION 2 question (new conversation, no session 1 transcript) ===")
print(question)

print("\n--- A) no memory ---")
print(chat(question))

stored_facts = json.load(open(STORE))
print("\n--- B) with semantic facts loaded from the store ---")
print("loaded facts:", stored_facts)
fact_lines = "\n".join(f"- {k}: {v}" for k, v in stored_facts.items())
print(chat(
    "Known facts about this person:\n" + fact_lines +
    "\n\nUsing only these facts, answer briefly.\n\n" + question
))
