"""Clean vs. confusion (irrelevant extras) vs. clash (contradictory memos), on local Ollama models.
Run: uv run examples/what-context-distraction-confusion-and-clash-are/confusion_clash_demo.py
"""
import json, re, sys, urllib.request

URL = "http://localhost:11434/api/chat"
MODELS = ["llama3.1:8b", "phi3:mini"]

# (entity, attribute phrase, old value, new value, unit word). Values are invented, so training can't help.
FACTS = [
    ("the Brelwick printer", "print speed", "12", "31", "pages per minute"),
    ("Dorvane Library", "closing hour", "6", "9", "o'clock in the evening"),
    ("the Quillon bridge", "weight limit", "8", "15", "tons"),
    ("Mapleford Bakery", "bread price", "4", "7", "dollars per loaf"),
    ("the Tessaly ferry", "crossing time", "20", "45", "minutes"),
    ("Harnok Gym", "locker count", "60", "140", "lockers"),
    ("the Vellum 5 camera", "battery life", "300", "520", "shots"),
    ("Pinegate Cinema", "screen count", "3", "9", "screens"),
]
# Unrelated memos of the same style, about other things.
FILLER_ENTITIES = ["Ostrava Pool", "the Kelmar tram", "Rowan Hotel", "the Zephra drone", "Lindenhall Museum",
                   "the Corvid 2 laptop", "Saltmarsh Cafe", "the Ibex train", "Wrenfield School", "the Mirage kettle"]
FILLER_ATTRS = ["opening hour", "ticket price", "seat count", "weight", "top speed", "room count", "warranty length",
                "capacity", "queue time", "height"]

def filler(n):
    out, k = [], 0
    while len(out) < n:
        e, a = FILLER_ENTITIES[k % len(FILLER_ENTITIES)], FILLER_ATTRS[(k * 3 + 1) % len(FILLER_ATTRS)]
        out.append(f"Memo {len(out)+1}: {e} has a {a} of {(k * 37) % 90 + 11}.")
        k += 1
    return out

def ask(model, prompt):
    body = {"model": model, "stream": False, "options": {"temperature": 0},
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=900))["message"]["content"]

def numbers(text):
    return re.findall(r"\d+", text.replace(",", ""))

def prompts(f, i):
    ent, attr, old, new, unit = f
    q = f"Question: what is the {attr} of {ent}? Answer with the number and unit only."
    clean = f"Memo: {ent} has a {attr} of {new} {unit}.\n\n{q}"
    fill = filler(40)
    fill.insert(20 + i % 5, f"Memo: {ent} has a {attr} of {new} {unit}.")
    confusion = "\n".join(fill) + f"\n\n{q}"
    clash = (f"Memo from the boss (Monday): {ent} has a {attr} of {old} {unit}.\n"
             f"Memo from the boss (Friday): correction, {ent} has a {attr} of {new} {unit}.\n\n"
             f"{q} If the memos disagree, use the most recent one.")
    # Harder clash: no instruction on which memo wins.
    clash_bare = (f"Memo from the boss (Monday): {ent} has a {attr} of {old} {unit}.\n"
                  f"Memo from the boss (Friday): correction, {ent} has a {attr} of {new} {unit}.\n\n{q}")
    # Hardest clash: the newer (Friday) memo is listed FIRST, so date and position disagree.
    clash_rev = (f"Memo from the boss (Friday): correction, {ent} has a {attr} of {new} {unit}.\n"
                 f"Memo from the boss (Monday): {ent} has a {attr} of {old} {unit}.\n\n{q}")
    return {"clean": clean, "confusion": confusion, "clash (told: newest wins)": clash, "clash (no hint)": clash_bare,
            "clash (newer listed 1st)": clash_rev}

def main():
    for model in (sys.argv[1:] or MODELS):
        score = {}
        print(f"\n=== {model} ===", flush=True)
        for i, f in enumerate(FACTS):
            for cond, p in prompts(f, i).items():
                ans = ask(model, p)
                nums = numbers(ans)
                ok = f[3] in nums and f[2] not in nums
                score[cond] = score.get(cond, 0) + ok
                print(f"[{cond:26}] {f[0]:22} expect {f[3]:>3} -> {'OK ' if ok else 'BAD'} | {ans.strip()[:70]!r}", flush=True)
        print(f"--- {model} correct out of {len(FACTS)} ---")
        for c, s in score.items():
            print(f"{c:26} {s}/{len(FACTS)}")

if __name__ == "__main__":
    main()
