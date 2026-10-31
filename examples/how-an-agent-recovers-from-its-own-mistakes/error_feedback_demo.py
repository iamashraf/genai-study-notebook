"""Does a descriptive tool error help an agent recover better than a vague one?

A strict tool, days_between(start_date, end_date), only accepts YYYYMMDD.
Each task states dates in messy human formats. The model gets up to 3 tool
calls. On a rejected call we return either a vague error ("error") or a
descriptive one. Success = an accepted call with the correct dates within 3 tries.
A call counts if it is a structured tool call, or if a strict extraction finds
one in the reply text (a JSON object naming days_between with both dates, or a
days_between(...) string). Extracted arguments go through the same checker and
must equal the expected dates, so text without the right YYYYMMDD dates fails.

Run: uv run examples/how-an-agent-recovers-from-its-own-mistakes/error_feedback_demo.py
"""
import json
import re
import sys
import urllib.request
from datetime import date

MODEL = "llama3.1:8b"
MAX_ATTEMPTS = 3
MAX_CALLS = 30  # hard cap: 5 tasks x 2 conditions x 3 attempts
calls_made = 0
# The tool description is silent about the format, like a poorly documented tool.

TOOL = {"type": "function", "function": {
    "name": "days_between",
    "description": "Count the days from start_date to end_date.",
    "parameters": {"type": "object", "required": ["start_date", "end_date"], "properties": {
        "start_date": {"type": "string"}, "end_date": {"type": "string"}}}}}

# (prompt, expected start, expected end)
TASKS = [
    ("How many days from 3rd March 2025 to 17th March 2025?", "20250303", "20250317"),
    ("How many days between 12/04/2025 and 30/04/2025? (day first)", "20250412", "20250430"),
    ("Count the days from Jan 5, 2025 to Feb 20, 2025.", "20250105", "20250220"),
    ("Days from 25.12.2024 to 06.01.2025? (day.month.year)", "20241225", "20250106"),
    ("How many days from 31 Oct 2025 to 15 Nov 2025?", "20251031", "20251115"),
]

ISO = re.compile(r"^\d{8}$")  # the tool wants YYYYMMDD, no dashes


def check(args, style):
    """Return (ok, error_message). ok means the strict tool accepts the call."""
    bad = [(k, args.get(k)) for k in ("start_date", "end_date")
           if not isinstance(args.get(k), str) or not ISO.match(args[k])]
    if not bad:
        try:
            for k in ("start_date", "end_date"):
                date(int(args[k][:4]), int(args[k][4:6]), int(args[k][6:]))
            return True, None
        except ValueError:
            bad = [("date", "invalid calendar date")]
    if style == "vague":
        return False, "error"
    return False, "; ".join(f"{k} must be YYYYMMDD with no separators (e.g. 20250303), got {v!r}" for k, v in bad)


def chat(messages):
    global calls_made
    calls_made += 1
    assert calls_made <= MAX_CALLS
    body = {"model": MODEL, "messages": messages, "tools": [TOOL], "stream": False,
            "options": {"temperature": 0, "seed": 1, "num_predict": 60}}
    req = urllib.request.Request("http://localhost:11434/api/chat", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=180))["message"]


def extract(text):
    """Find a days_between call in plain reply text. Returns args dict or None."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", text or ""):
        try:
            obj, _ = dec.raw_decode(text[m.start():])
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("name") == "days_between":
            a = obj.get("parameters", obj.get("arguments"))
            if isinstance(a, dict) and "start_date" in a and "end_date" in a:
                return a
    m = re.search(r"days_between\(\s*(?:start_date\s*=\s*)?[\"']([^\"']+)[\"']\s*,"
                  r"\s*(?:end_date\s*=\s*)?[\"']([^\"']+)[\"']\s*\)", text or "")
    return {"start_date": m.group(1), "end_date": m.group(2)} if m else None


def run_task(prompt, exp, style):
    messages = [{"role": "user", "content": prompt + " Use the days_between tool."}]
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            msg = chat(messages)
        except Exception as e:  # timeout etc.: record, never retry
            return False, attempt, f"timed out ({type(e).__name__})"
        calls = msg.get("tool_calls") or []
        if calls:
            args, how = calls[0]["function"]["arguments"], "structured"
            if isinstance(args, str):
                args = json.loads(args)
        else:
            args, how = extract(msg.get("content")), "extracted from text"
        if args is None:
            return False, attempt, "no tool call and nothing extractable"
        print(f"    attempt {attempt}: {how} {args}", flush=True)
        ok, err = check(args, style)
        if ok:
            good = (args["start_date"], args["end_date"]) == exp
            return good, attempt, "ok" if good else f"accepted wrong dates {args}"
        messages += [msg, {"role": "tool", "content": err}]
    return False, MAX_ATTEMPTS, f"gave up, last args {args}"


if __name__ == "__main__":
    totals = {}
    for style in ("vague", "descriptive"):
        print(f"\n=== error style: {style} ===", flush=True)
        wins = 0
        for i, (p, s_, e) in enumerate(TASKS):
            ok, tries, note = run_task(p, (s_, e), style)
            wins += ok
            print(f"  task {i+1}: {'PASS' if ok else 'FAIL'} tries={tries} {note}", flush=True)
        totals[style] = wins
        print(f"  {wins}/{len(TASKS)} tasks succeeded within {MAX_ATTEMPTS} attempts", flush=True)
    print(f"\nmodel calls used: {calls_made}/{MAX_CALLS}")
