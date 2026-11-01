"""Can a model actually tell these seven kinds of memory apart, given only a
one-line definition of each? Classifies seven statements (one per type) and
checks the predicted label against the expected one."""
import json, urllib.request

OLLAMA = "http://localhost:11434"
MODEL = "llama3.1:8b"

TYPES = {
    "working": "something happening in the current task, right now, not stored for later",
    "semantic": "a durable fact the speaker just knows, with no memory of when they learned it",
    "episodic": "a specific past event: what happened, when, and how it went",
    "procedural": "a routine or method the speaker runs on autopilot",
    "retrieval": "something explicitly looked up from an outside source, not memorized",
    "parametric": "general knowledge the speaker already had before this job, not specific to it",
    "prospective": "a commitment to do something later, triggered by a future event",
}

EXAMPLES = [
    ("Hold on, let me finish typing up these standup notes before we move on.", "working"),
    ("The design lead is based in Austin.", "semantic"),
    ("Last Tuesday's deploy got rolled back because of a cache bug.", "episodic"),
    ("Every Friday I run the same release checklist: freeze the branch, tag it, notify the channel.", "procedural"),
    ("Let me look up the on-call rotation in the wiki, I don't have it memorized.", "retrieval"),
    ("I already know how REST APIs generally work, nobody taught me that here.", "parametric"),
    ("Remind me to check the ticket again once QA signs off.", "prospective"),
]


def classify(statement):
    prompt = (
        "Here are seven kinds of memory, each with a one-line definition:\n"
        + "\n".join(f"- {k}: {v}" for k, v in TYPES.items())
        + f"\n\nWhich ONE kind does this statement reflect: \"{statement}\"\n"
        + "Reply with exactly one word: the type name, nothing else."
    )
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
    reply = json.load(urllib.request.urlopen(req, timeout=300))["message"]["content"]
    return reply.strip().lower().strip(".")


correct = 0
for statement, expected in EXAMPLES:
    predicted = classify(statement)
    hit = predicted == expected
    correct += hit
    print(f"[{'OK' if hit else 'MISS'}] expected={expected:<11} predicted={predicted:<11} \"{statement}\"")

print(f"\n{correct}/{len(EXAMPLES)} correct")
