# /// script
# dependencies = ["tiktoken"]
# ///
"""Backs the claims in posts/why-agent-loops-need-stop-conditions.md.
Run with: uv run examples/why-agent-loops-need-stop-conditions/stop_conditions_demo.py

Requires a local Ollama server (http://localhost:11434) with llama3.1:8b pulled.

A tiny agent loop whose only tool, lookup_record, ALWAYS fails (the record does
not exist). Run A has no stop rule except a 15-step safety cutoff of our own.
Run B adds max_steps=4 and repeated-identical-call detection (halt when the same
call is made a 3rd time). Token counts use tiktoken's cl100k_base as an
approximation (llama3.1 has its own tokenizer, so treat as ballpark).
"""
import json
import urllib.request
import tiktoken

ENC = tiktoken.get_encoding("cl100k_base")
SYSTEM = (
    "You are a support agent. Goal: find the shipping address for order record 4471.\n"
    "Tools: lookup_record(id) -> returns the record or an error.\n"
    'Reply with ONLY one JSON object. To call the tool: {"action":"lookup_record","id":"<id>"}. '
    'When finished: {"action":"done","answer":"<text>"}.'
)


# Scenario 1: a clear error. Scenario 2: a vague "temporary" error plus a persistent
# prompt -- the kind of setup that makes real agents retry. The tool fails in BOTH.
PERSIST = ("\nThe record definitely exists. Never give up and never answer 'done' "
           "until you have the address; if a lookup fails, try again.")
MODE = {"msg": "ERROR: record {rid} not found"}


def tool_lookup_record(rid):
    return MODE["msg"].format(rid=rid)  # always fails, by design


def chat(messages):
    body = json.dumps({"model": "llama3.1:8b", "messages": messages, "stream": False,
                       "format": "json", "options": {"temperature": 0}}).encode()
    req = urllib.request.Request("http://localhost:11434/api/chat", body,
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["message"]["content"]


def ntok(messages):
    return sum(len(ENC.encode(m["content"])) for m in messages)


def run(label, hard_cap, max_steps=None, repeat_limit=None, persistent=False):
    print(f"\n=== {label} ===")
    msgs = [{"role": "system", "content": SYSTEM + (PERSIST if persistent else "")},
            {"role": "user", "content": "Find the shipping address for record 4471."}]
    seen, total_in, reason = {}, 0, None
    for step in range(1, hard_cap + 1):
        if max_steps and step > max_steps:
            reason = f"max_steps={max_steps} reached"; break
        ctx = ntok(msgs); total_in += ctx
        reply = chat(msgs)
        try:
            act = json.loads(reply)
        except json.JSONDecodeError:
            act = {"action": "?"}
        key = json.dumps(act, sort_keys=True)
        seen[key] = seen.get(key, 0) + 1
        print(f"step {step:2d} | context {ctx:4d} tok | model: {reply.strip()}")
        if act.get("action") == "done":
            reason = "model said done"; break
        if repeat_limit and seen[key] >= repeat_limit:
            reason = f"same call made {seen[key]} times"; break
        result = tool_lookup_record(act.get("id", "?"))
        print(f"        tool -> {result}")
        msgs += [{"role": "assistant", "content": reply},
                 {"role": "user", "content": f"Tool result: {result}"}]
    else:
        reason = f"safety cutoff of {hard_cap} steps (nothing else stopped it)"
    print(f"STOPPED: {reason}")
    print(f"steps run: {step if not reason.startswith('max_steps') else step-1} | "
          f"total input tokens processed across all calls: {total_in}")


run("0: clear error, plain prompt, no stop rule (own cutoff = 15)", hard_cap=15)
MODE["msg"] = "ERROR: temporary lookup failure for record {rid}, please retry"
run("A: vague error + persistent prompt, no stop rule (own cutoff = 15)", hard_cap=15, persistent=True)
run("B: same setup, max_steps=4 + repeat detection (3rd identical call)", hard_cap=15,
    max_steps=4, repeat_limit=3, persistent=True)
