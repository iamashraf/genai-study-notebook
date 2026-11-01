"""Episodic memory is a record of a SPECIFIC past attempt and its outcome, not a
flat fact. We log three past venue-booking episodes, score each one the way Park
et al. (2023) score memories for retrieval -- recency, importance, relevance --
then combine the three into one retrieval score and see which episode surfaces
for a new booking. Finally we show the agent using that one retrieved episode to
avoid repeating the same mistake."""
import json, math, re, urllib.request

OLLAMA = "http://localhost:11434"
MODEL = "llama3.1:8b"


def post(path, body):
    req = urllib.request.Request(OLLAMA + path, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))


def chat(prompt):
    r = post("/api/chat", {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                           "stream": False, "options": {"temperature": 0}})
    return r["message"]["content"].strip()


def embed(text):
    return post("/api/embeddings", {"model": "nomic-embed-text", "prompt": text})["embedding"]


def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (math.hypot(*a) * math.hypot(*b))


def min_max(values):
    lo, hi = min(values), max(values)
    if hi == lo:
        return [1.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


# ---- three past episodes: a specific attempt + what went wrong, each with how
# long ago it happened. This is what makes them episodic rather than a semantic
# fact like "venues need parking" -- each one is one dated, concrete experience.
episodes = [
    {"text": "Tried booking Riverside Hall for the Saturday team offsite. It turned out "
             "to be closed for renovation that weekend, and finding a backup venue on "
             "short notice ate up a full hour.",
     "days_ago": 30},
    {"text": "Booked the Garden Room at Oakwood Inn for a client dinner. There was no "
             "parking nearby, so three guests arrived 20 minutes late.",
     "days_ago": 10},
    {"text": "Reserved the Hotel Meridian conference room for the quarterly review. "
             "The Wi-Fi dropped twice during the video call and the meeting had to be "
             "rescheduled.",
     "days_ago": 2},
]

query = "I need to book a venue for this Saturday's team offsite."

print("=== PAST EPISODES IN MEMORY ===")
for e in episodes:
    print(f" - ({e['days_ago']}d ago) {e['text']}")

# -- recency: exponential decay over days since the episode happened, same shape
# as Park et al.'s decay over hours since last retrieved (they use 0.995/hour) --
DECAY = 0.98
recency_raw = [DECAY ** e["days_ago"] for e in episodes]

# -- importance: ask the model to rate how costly the mistake was, 1-10, the
# same "poignancy" framing Park et al. use for their importance score --
importance_raw = []
for e in episodes:
    rating = chat(
        "On a scale of 1 to 10, where 1 is a minor inconvenience and 10 is a major "
        "failure that derailed the plan, rate how costly the following work mistake "
        "was. Reply with ONLY the integer.\n\n"
        f"Mistake: {e['text']}\nRating:"
    )
    match = re.search(r"\d+", rating)
    score = float(match.group()) if match else 5.0
    print(f"  importance raw reply: {rating!r} -> {score}")
    importance_raw.append(score)

# -- relevance: cosine similarity between the episode's embedding and the query's --
query_vec = embed(query)
relevance_raw = [cos(embed(e["text"]), query_vec) for e in episodes]

print("\n=== RAW SCORES BEFORE NORMALIZING ===")
for i, e in enumerate(episodes):
    print(f"  #{i+1} recency={recency_raw[i]:.4f} importance={importance_raw[i]:.1f} relevance={relevance_raw[i]:.4f}")

recency_n = min_max(recency_raw)
importance_n = min_max(importance_raw)
relevance_n = min_max(relevance_raw)

print("\n=== RETRIEVAL SCORES (each column rescaled 0-1 within these 3 episodes, "
      "combined = equal-weighted average) ===")
print(f"{'episode':<10}{'recency':>10}{'importance':>12}{'relevance':>11}{'combined':>10}")
scored = []
for i, e in enumerate(episodes):
    combined = (recency_n[i] + importance_n[i] + relevance_n[i]) / 3
    scored.append((combined, e))
    print(f"{'#'+str(i+1):<10}{recency_n[i]:>10.2f}{importance_n[i]:>12.2f}{relevance_n[i]:>11.2f}{combined:>10.2f}")

scored.sort(key=lambda t: -t[0])
top_score, top_episode = scored[0]
print(f"\nTop-ranked episode by combined score ({top_score:.2f}): {top_episode['text']}")

recency_top = episodes[recency_n.index(max(recency_n))]
relevance_top = episodes[relevance_n.index(max(relevance_n))]
print(f"Top-ranked episode by recency alone: {recency_top['text'][:60]}...")
print(f"Top-ranked episode by relevance alone: {relevance_top['text'][:60]}...")

print("\n=== NEW SITUATION ===")
print(query)

print("\n--- A) no episodic memory ---")
print(chat(f"{query} What should I check before booking? Answer in 2-3 sentences."))

print("\n--- B) with the retrieved episode ---")
print(chat(
    "Here is a specific past episode from memory:\n"
    f"\"{top_episode['text']}\"\n\n"
    f"New situation: {query}\n"
    "Using what happened in that past episode, what should I check before booking "
    "this time, and why? Answer in 2-3 sentences."
))
