"""Two fresh "sessions" with a stateless model. Session 2 is asked a question
that needs facts only mentioned in session 1; we answer it with and without a
tiny external memory store (a JSON file + embedding lookup)."""
import json, math, os, tempfile, urllib.request

OLLAMA = "http://localhost:11434"
MODEL = "llama3.1:8b"
STORE = os.path.join(tempfile.gettempdir(), "agent_memory_demo.json")


def post(path, body):
    req = urllib.request.Request(OLLAMA + path, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))


def chat(messages):
    r = post("/api/chat", {"model": MODEL, "messages": messages, "stream": False,
                           "options": {"temperature": 0}})
    return r["message"]["content"].strip()


def embed(text):
    return post("/api/embeddings", {"model": "nomic-embed-text", "prompt": text})["embedding"]


def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (math.hypot(*a) * math.hypot(*b))


# ---- the memory store: save notes to a JSON file, retrieve the closest ones ----
def save_notes(notes):
    with open(STORE, "w") as f:
        json.dump([{"note": n, "vec": embed(n)} for n in notes], f)


def recall(query, k=2):
    items = json.load(open(STORE))
    q = embed(query)
    return [i["note"] for i in sorted(items, key=lambda i: -cos(q, i["vec"]))[:k]]


# ---- Session 1 ----
session1 = [
    "Hi! I'm Priya. I run a team of 7 people in Lisbon.",
    "Quick heads up: one of my teammates, Tomas, has a severe peanut allergy.",
    "Our budget for team meals is 25 euros per person.",
]
print("=== SESSION 1 (user messages) ===")
for m in session1:
    print(" -", m)
transcript = "\n".join(session1)
extracted = chat([{"role": "user", "content":
    "Read this chat and write each durable fact worth remembering as one short "
    "line, one fact per line, no bullets or numbering, nothing else.\n\n" + transcript}])
notes = [l.strip() for l in extracted.splitlines() if l.strip()]
print("\n=== NOTES THE AGENT WROTE TO ITS MEMORY FILE ===")
for n in notes:
    print(" -", n)
save_notes(notes)
# session 1 ends: its context window is gone. Only the JSON file remains.

# ---- Session 2: brand-new context, nothing carried over ----
question = ("I'm booking our team dinner for Friday. Which city should I search in, "
            "how many seats do I need, what is the max total budget, and what must the restaurant avoid?")
print("\n=== SESSION 2 question ===\n", question)

print("\n--- A) no memory ---")
print(chat([{"role": "user", "content": question}]))

hits = recall(question, k=3)
print("\n--- B) with retrieved notes injected ---")
print("retrieved:", hits)
print(chat([{"role": "user", "content":
    "Notes from earlier sessions with this user:\n" + "\n".join("- " + h for h in hits)
    + "\n\nUsing the notes, answer briefly.\n\n" + question}]))
