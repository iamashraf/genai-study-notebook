"""Preload-everything vs just-in-time context, on 8 small docs and 5 questions (llama3.1:8b via Ollama).
Run: uv run examples/what-just-in-time-context-is/jit_context_demo.py"""
import json, tempfile, urllib.request, pathlib
import tiktoken

MODEL = "llama3.1:8b"
enc = tiktoken.get_encoding("cl100k_base")
ntok = lambda s: len(enc.encode(s))

# (filename, one-line description, body). Each body holds one distinctive fact plus filler detail.
FILL = " Staff are expected to follow the standard process, keep records for audit, and raise questions with their team lead. Exceptions need written approval from a manager, and the policy is reviewed once a year by the operations group."
DOCS = [
 ("vacation_policy.txt", "How much paid vacation employees get", "Vacation policy. Full-time employees receive 24 days of paid vacation per year, accruing monthly. Up to 5 unused days may be carried into the next year." + FILL * 3),
 ("expense_policy.txt", "Rules for claiming work expenses", "Expense policy. Meals on business trips are reimbursed up to 60 dollars per day. Receipts are required for any single item above 25 dollars. Claims must be filed within 30 days." + FILL * 3),
 ("security_policy.txt", "Passwords, laptops and account security", "Security policy. Passwords must be rotated every 90 days and be at least 14 characters long. Laptops use full-disk encryption and lock after 5 minutes idle." + FILL * 3),
 ("remote_work.txt", "Working from home rules", "Remote work policy. Employees may work remotely up to 3 days per week. The home office stipend is 400 dollars, paid once at the start of employment." + FILL * 3),
 ("onboarding.txt", "What happens in a new hire's first weeks", "Onboarding guide. New hires receive their laptop on day 1 and meet their buddy in week 1. The probation review takes place after 60 days." + FILL * 3),
 ("support_sla.txt", "Customer support response targets", "Support SLA. Critical tickets get a first response within 1 hour. Normal tickets get a first response within 8 business hours. Weekend coverage is limited to critical tickets." + FILL * 3),
 ("release_process.txt", "How software releases are shipped", "Release process. Production releases ship every Tuesday at 10:00 UTC. A release needs two approving reviews and a green test run. Rollbacks are done by the on-call engineer." + FILL * 3),
 ("travel_policy.txt", "Booking flights and hotels for travel", "Travel policy. Flights must be booked at least 14 days ahead in economy class. Hotel stays are capped at 180 dollars per night." + FILL * 3),
]
QA = [
 ("How many paid vacation days does a full-time employee get per year?", "24"),
 ("How often must passwords be rotated?", "90"),
 ("What day of the week do production releases ship?", "tuesday"),
 ("What is the home office stipend?", "400"),
 ("What is the nightly hotel cap for travel?", "180"),
]

def chat(prompt):
    body = json.dumps({"model": MODEL, "stream": False, "options": {"temperature": 0},
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("http://localhost:11434/api/chat", body, {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["message"]["content"].strip()

d = pathlib.Path(tempfile.mkdtemp())
for name, _, body in DOCS:
    (d / name).write_text(body)
catalogue = "\n".join(f"- {n}: {desc}" for n, desc, _ in DOCS)
print(f"8 docs on disk; full text = {sum(ntok((d/n).read_text()) for n,_,_ in DOCS)} tokens; catalogue alone = {ntok(catalogue)} tokens\n")

tot = {"A": [0, 0], "B": [0, 0]}  # tokens, correct
for q, key in QA:
    # Strategy A: preload everything
    everything = "\n\n".join(f"[{n}]\n{(d/n).read_text()}" for n, _, _ in DOCS)
    pa = f"Answer using only these documents.\n\n{everything}\n\nQuestion: {q}\nAnswer briefly."
    ans_a = chat(pa)
    # Strategy B: call 1 picks a file from the catalogue, call 2 answers with only that file loaded
    p1 = f"Files available:\n{catalogue}\n\nQuestion: {q}\nReply with only the single filename needed to answer."
    pick = chat(p1).strip("`'\" -")
    names = [n for n, _, _ in DOCS]
    pick = next((n for n in names if n in pick), None)
    p2 = f"Answer using only this document.\n\n[{pick}]\n{(d/pick).read_text() if pick else ''}\n\nQuestion: {q}\nAnswer briefly."
    ans_b = chat(p2)
    ta, tb = ntok(pa), ntok(p1) + ntok(p2)
    ca, cb = key in ans_a.lower(), key in ans_b.lower()
    tot["A"][0] += ta; tot["A"][1] += ca; tot["B"][0] += tb; tot["B"][1] += cb
    print(f"Q: {q}\n  A (preload all): {ta} tokens, 1 call, correct={ca} -> {ans_a}\n  B (just-in-time): {tb} tokens, 2 calls, opened={pick}, correct={cb} -> {ans_b}\n")
print(f"TOTAL A: {tot['A'][0]} tokens, {tot['A'][1]}/5 correct")
print(f"TOTAL B: {tot['B'][0]} tokens, {tot['B'][1]}/5 correct")
