"""Two structurally similar venue-booking tasks. The agent solves the first
one from scratch, then writes down the general method it used (not the
specific answer) as a reusable "skill" -- a tiny stand-in for Voyager's skill
library. For the second task, we retrieve that skill by embedding similarity
and hand it to the model as a shortcut, instead of letting it re-derive the
method. A ground-truth Python check (not the model) decides who is correct."""
import json, math, urllib.request

OLLAMA = "http://localhost:11434"
MODEL = "llama3.1:8b"


def post(path, body):
    req = urllib.request.Request(OLLAMA + path, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))


def chat(prompt):
    r = post("/api/chat", {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                           "stream": False, "options": {"temperature": 0}})
    return r["message"]["content"].strip(), r.get("eval_count")


def embed(text):
    return post("/api/embeddings", {"model": "nomic-embed-text", "prompt": text})["embedding"]


def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / (math.hypot(*a) * math.hypot(*b))


# ---- ground truth: ordinary Python, not the model. "available" already
# means "available on the specific date being asked about" for that task,
# like a real booking API would return. ----
TASK1_VENUES = [
    {"name": "Northside Barn",  "area": "Northside", "capacity": 20, "price": 10, "available": True},
    {"name": "Garden Hall",     "area": "Riverside",  "capacity": 3,  "price": 12, "available": True},
    {"name": "Oak Room",        "area": "Riverside",  "capacity": 12, "price": 18, "available": False},
    {"name": "River Pavilion",  "area": "Riverside",  "capacity": 12, "price": 30, "available": True},
    {"name": "Elm Hall",        "area": "Riverside",  "capacity": 12, "price": 45, "available": True},
]
TASK2_VENUES = [
    {"name": "Westside Barn",    "area": "Westside", "capacity": 20, "price": 8,  "available": True},
    {"name": "Downtown Studio",  "area": "Downtown", "capacity": 2,  "price": 10, "available": True},
    {"name": "Lakeside Room",    "area": "Downtown", "capacity": 12, "price": 16, "available": False},
    {"name": "City Center Hall", "area": "Downtown", "capacity": 12, "price": 22, "available": True},
    {"name": "Metro Hall",       "area": "Downtown", "capacity": 12, "price": 33, "available": True},
]


def ground_truth(venues, area, headcount):
    candidates = [v for v in venues if v["area"] == area and v["capacity"] >= headcount and v["available"]]
    return min(candidates, key=lambda v: v["price"]) if candidates else None


# The table hands back pre-computed Yes/No flags for "meets headcount" and
# "available", the way a real booking API would, instead of a raw capacity
# number the model would have to compare itself (that numeric comparison is
# where a small local model is unreliable, and testing that isn't the point
# of this demo -- following a known filter-then-sort method is).
def table_text(venues, headcount):
    lines = ["name | area | meets headcount | available for the requested date | price"]
    for v in venues:
        meets = "Yes" if v["capacity"] >= headcount else "No"
        lines.append(f"{v['name']} | {v['area']} | {meets} | {'Yes' if v['available'] else 'No'} | {v['price']}")
    return "\n".join(lines)


def ask_venue_question(venues, area, headcount, procedure=None):
    instructions = f"Follow this known procedure to answer:\n{procedure}\n\n" if procedure else ""
    prompt = (
        f"{instructions}Here is a venue table:\n{table_text(venues, headcount)}\n\n"
        f"Question: find the cheapest venue in the {area} area that meets the headcount and is available "
        f"for the requested date.\n\n"
        f"Work through it in exactly this format, filling in each blank:\n"
        f"Step 1 - venues in the {area} area: <list names>\n"
        f"Step 2 - of those, where meets headcount is Yes: <list names>\n"
        f"Step 3 - of those, where available is Yes: <list names>\n"
        f"Step 4 - cheapest of those: <name and price>\n"
        f"ANSWER: <venue name>"
    )
    reply, tokens = chat(prompt)
    answer_line = [l for l in reply.splitlines() if l.strip().upper().startswith("ANSWER:")]
    picked = answer_line[-1].split(":", 1)[1].strip() if answer_line else None
    return reply, picked, tokens


def leaked(procedure, terms):
    low = procedure.lower()
    return [t for t in terms if t.lower() in low]


# ---- Task 1: solved from scratch ----
print("=== TASK 1: Riverside, headcount 7 ===")
print(table_text(TASK1_VENUES, 7))
reply1, picked1, tokens1 = ask_venue_question(TASK1_VENUES, "Riverside", 7)
truth1 = ground_truth(TASK1_VENUES, "Riverside", 7)
print(reply1)
print(f"\nmodel picked: {picked1}   ground truth: {truth1['name']} (${truth1['price']})   "
      f"correct: {picked1 == truth1['name']}   output tokens: {tokens1}")

# ---- Ask the model for the reusable method, not the specific answer ----
print("\n=== Asking for the general reusable procedure (not the specific answer) ===")
procedure_prompt = (
    "You just solved a venue-booking task in four steps. Write down the GENERAL method you used, as a "
    "short numbered list of steps, so it could be reused for ANY similar venue request with a different "
    "area and headcount. Do not mention Riverside, the number 7, or any specific venue name or price. "
    "Describe only the general steps, using placeholder words like 'the area' and 'the headcount'."
)
procedure, _ = chat(procedure_prompt)
leaks = leaked(procedure, ["Riverside", "River Pavilion", "35"])
if leaks:
    print(f"(leak detected: {leaks} -- re-prompting once)")
    procedure, _ = chat(procedure_prompt + " Remember: use only placeholder words, never the actual "
                         "values from the task you just solved.")
    leaks = leaked(procedure, ["Riverside", "River Pavilion", "35"])
print(procedure)
print(f"\nleaked task-specific details after final check: {leaks if leaks else 'none'}")

# ---- Save it as a stored skill, plus one unrelated distractor skill ----
SKILLS = [
    {
        "desc": "finding the cheapest available venue that matches an area and a headcount",
        "procedure": procedure,
    },
    {
        "desc": "splitting a shared dinner bill fairly among people who ordered different amounts",
        "procedure": ("1. List each person's items and their cost.\n"
                       "2. Sum each person's subtotal.\n"
                       "3. Split tax and tip proportionally to each subtotal.\n"
                       "4. Report what each person owes in total."),
    },
]
for s in SKILLS:
    s["vec"] = embed(s["desc"])

# ---- Task 2: a structurally similar but different request ----
print("\n=== TASK 2: Downtown, headcount 5 ===")
print(table_text(TASK2_VENUES, 5))
truth2 = ground_truth(TASK2_VENUES, "Downtown", 5)
task2_question = "find the cheapest venue in the Downtown area, with capacity for at least 5 people, that is available for the requested date"

print("\n--- A) baseline: solved from scratch, no stored procedure ---")
reply2a, picked2a, tokens2a = ask_venue_question(TASK2_VENUES, "Downtown", 5)
print(reply2a)
print(f"\nmodel picked: {picked2a}   ground truth: {truth2['name']} (${truth2['price']})   "
      f"correct: {picked2a == truth2['name']}   output tokens: {tokens2a}")

print("\n--- retrieving the closest stored skill by embedding similarity ---")
q = embed(task2_question)
scored = sorted(SKILLS, key=lambda s: -cos(q, s["vec"]))
for s in scored:
    print(f"  similarity {cos(q, s['vec']):.3f}  -  {s['desc']}")
best = scored[0]

print("\n--- B) with the retrieved procedure handed to the model as a shortcut ---")
reply2b, picked2b, tokens2b = ask_venue_question(TASK2_VENUES, "Downtown", 5, procedure=best["procedure"])
print(reply2b)
print(f"\nmodel picked: {picked2b}   ground truth: {truth2['name']} (${truth2['price']})   "
      f"correct: {picked2b == truth2['name']}   output tokens: {tokens2b}")

print("\n=== SUMMARY ===")
print(f"Task 1 (from scratch):             correct={picked1 == truth1['name']}, output tokens={tokens1}")
print(f"Task 2 A (from scratch, no skill):  correct={picked2a == truth2['name']}, output tokens={tokens2a}")
print(f"Task 2 B (reused stored procedure): correct={picked2b == truth2['name']}, output tokens={tokens2b}")
