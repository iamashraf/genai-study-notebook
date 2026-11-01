"""One CoALA-style decision cycle for a single venue-booking task.

Cycle 1, planning: a retrieval action pulls the team-size fact from semantic
memory. The procedural recipe (filter by capacity and availability, sort by
price) runs as plain code, the "explicit knowledge written in the agent's
code" form of procedural memory CoALA names (see post, Sources [1]), rather
than as a string fed to the model. The episodic note is retrieved and handed
to the LLM as the one judgment call left: does anything in working memory
rule out the cheapest option. That reasoning action is the actual model call.
Cycle 1, execution: a grounding action (the recommendation) goes out, and a
stub observation comes back.
Cycle 2: a learning action writes the outcome back to episodic memory.

An ablation re-runs the reasoning action with the episodic note left out of
working memory, to show the final pick depends on what's in working memory,
not just on asking the model to pick a venue.
"""
import json, urllib.request

OLLAMA = "http://localhost:11434"
MODEL = "llama3.1:8b"


def chat(prompt):
    req = urllib.request.Request(
        OLLAMA + "/api/chat",
        json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                    "stream": False, "options": {"temperature": 0}}).encode(),
        {"Content-Type": "application/json"},
    )
    r = json.load(urllib.request.urlopen(req, timeout=300))
    return r["message"]["content"].strip()


VENUES = [
    {"name": "Downtown Studio", "capacity": 10, "available": True, "price": 18},
    {"name": "Lakeside Room", "capacity": 12, "available": True, "price": 20},
    {"name": "City Center Hall", "capacity": 8, "available": True, "price": 22},
    {"name": "Metro Hall", "capacity": 3, "available": True, "price": 15},
    {"name": "Harbor Loft", "capacity": 20, "available": False, "price": 12},
]

# -- the three long-term stores, each a plain Python value living outside the
#    prompt until a retrieval action pulls it in --
semantic_memory = {"team_size": 7}
procedural_memory = ("filter venues by capacity >= team size, then by availability, "
                      "then sort what's left by price ascending")
episodic_memory = ["Last booking at Downtown Studio had a Wi-Fi outage during the event."]
FLAGGED_VENUE = "Downtown Studio"  # the venue the episodic note above refers to


def retrieve_shortlist():
    """Retrieve the semantic fact, then apply procedural memory's code form
    (the filter-and-sort recipe) to produce the shortlist for working memory."""
    fits = [v for v in VENUES if v["capacity"] >= semantic_memory["team_size"] and v["available"]]
    fits.sort(key=lambda v: v["price"])
    return fits


def ground_truth(shortlist, use_episodic=True):
    options = shortlist
    if use_episodic:
        options = [v for v in options if v["name"] != FLAGGED_VENUE]
    return options[0]["name"], options[0]["price"]


def build_prompt(shortlist, include_episodic):
    facts = [
        f"- semantic memory (already applied): team size is {semantic_memory['team_size']} people",
        f"- procedural memory (already applied): {procedural_memory}",
    ]
    if include_episodic:
        facts.append(f"- episodic memory: {episodic_memory[0]}")
    listing = "\n".join(f"- {v['name']}: ${v['price']}" for v in shortlist)
    return (
        "Task: recommend one venue to book for our team.\n\n"
        "Working memory this cycle:\n" + "\n".join(facts) + "\n\n"
        "Shortlist, already filtered by capacity and availability, sorted cheapest first:\n"
        + listing + "\n\n"
        "Rule: if working memory above includes an episodic note reporting a past problem at a "
        "venue, treat that venue as disqualified, no matter how cheap it is. Pick the cheapest "
        "venue on the shortlist that is not disqualified. State which venue you picked and why "
        "in one sentence. End with a line exactly like:\nANSWER: <venue name>\n"
    )


def extract_answer(response):
    for line in response.splitlines():
        if line.strip().upper().startswith("ANSWER:"):
            return line.split(":", 1)[1].strip()
    return None


def run_cycle(shortlist, include_episodic, label):
    prompt = build_prompt(shortlist, include_episodic)
    response = chat(prompt)
    pick = extract_answer(response)
    gt_name, gt_price = ground_truth(shortlist, use_episodic=include_episodic)
    print(f"\n--- {label} ---")
    print(response)
    print(f"model picked: {pick}   ground truth: {gt_name} (${gt_price})   correct: {pick == gt_name}")
    return pick


print("=== CYCLE 1 - PLANNING (retrieval actions) ===")
print("\n[retrieval -> semantic memory]")
print(semantic_memory)
print("\n[retrieval -> procedural memory]")
print(procedural_memory)
print("\n[retrieval -> episodic memory]")
for e in episodic_memory:
    print(" -", e)

shortlist = retrieve_shortlist()
print("\n[semantic + procedural memory applied -> shortlist pulled into working memory]")
for v in shortlist:
    print(" -", v["name"], f"(${v['price']})")

print("\n[working memory prompt assembled from all three stores]")
full_prompt = build_prompt(shortlist, include_episodic=True)
print(full_prompt)

print("\n[reasoning action -> model response, run 3 times for stability]")
picks = [run_cycle(shortlist, True, f"run {i+1}") for i in range(3)]

print("\n=== CYCLE 1 - EXECUTION (grounding action) ===")
final_pick = picks[-1]
print(f"[grounding action -> recommend '{final_pick}' to the user]")
print("[observation from environment -> user confirms the booking]")

print("\n=== CYCLE 2 - LEARNING (write to episodic memory) ===")
print("episodic memory before:", episodic_memory)
episodic_memory.append(
    f"Booking at {final_pick} for {semantic_memory['team_size']} people confirmed, no issues reported."
)
print("episodic memory after:", episodic_memory)

print("\n=== ABLATION - same cycle, episodic note left out of working memory ===")
ablation_pick = run_cycle(shortlist, False, "episodic note omitted")
print(f"\nwith episodic memory in working memory, picked: {final_pick}")
print(f"with episodic memory left out, picked: {ablation_pick}")
