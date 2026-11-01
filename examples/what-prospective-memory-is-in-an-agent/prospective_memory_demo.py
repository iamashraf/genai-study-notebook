"""A deferred intention tied to a future trigger, stored outside the context
window and checked later -- not a fact (semantic), not a past event (episodic),
not a how-to (procedural).

Run as separate process invocations, like a real agent and a later cron tick
would be separate processes with no shared memory except the file on disk:

    uv run examples/what-prospective-memory-is-in-an-agent/prospective_memory_demo.py session
    uv run examples/what-prospective-memory-is-in-an-agent/prospective_memory_demo.py tick running
    uv run examples/what-prospective-memory-is-in-an-agent/prospective_memory_demo.py tick finished
    uv run examples/what-prospective-memory-is-in-an-agent/prospective_memory_demo.py tick finished

`session` asks the model to turn a user request into a structured record --
label, trigger, action -- mirroring PM-Bench's task schema of "a
natural-language label, a trigger condition, and an executable action", and
saves it to an external JSON store. That process then exits.

Each `tick <deploy_status>` is a brand-new process. It has no memory of the
session; it only loads the stored record and compares the trigger to a
simulated current state. Only when the trigger is actually met does it build
a fresh prompt from the stored record (no session history) and call the
model to perform the deferred action.
"""
import json, os, sys, tempfile, urllib.request

OLLAMA = "http://localhost:11434"
MODEL = "llama3.1:8b"
STORE = os.path.join(tempfile.gettempdir(), "prospective_memory_demo.json")


def post(path, body):
    req = urllib.request.Request(OLLAMA + path, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))


def chat(messages, json_mode=False):
    body = {"model": MODEL, "messages": messages, "stream": False,
            "options": {"temperature": 0}}
    if json_mode:
        body["format"] = "json"
    r = post("/api/chat", body)
    return r["message"]["content"].strip()


def save_record(record):
    json.dump(record, open(STORE, "w"))


def load_record():
    return json.load(open(STORE))


def run_session():
    """Process 1: extract the deferred intention and persist it. The model
    fills in the values; the record's keys are fixed by this prompt, not
    chosen by the model."""
    user_message = "Once the deploy finishes, tell me the result and whether we need to roll back."
    print("=== SESSION (user message) ===")
    print(" -", user_message)

    extraction_prompt = (
        "A user said this to an agent: \"" + user_message + "\"\n\n"
        "This is a deferred intention: something to do later, triggered by a future "
        "event, not something to do now. Extract it as JSON with exactly these keys:\n"
        '  "label": short name for the task\n'
        '  "trigger_state_key": the state field to watch (e.g. "deploy_status")\n'
        '  "trigger_value": the value that state field must equal for the trigger to fire\n'
        '  "action_text": what the agent should do when the trigger fires\n'
        '  "status": always "pending"\n'
        "Return only the JSON object."
    )
    record = json.loads(chat([{"role": "user", "content": extraction_prompt}], json_mode=True))
    print("\n=== INTENTION WRITTEN TO EXTERNAL STORE ===")
    print(json.dumps(record, indent=2))
    save_record(record)
    # This process exits here. Its conversation is gone. Only the file on
    # disk survives into the next process.


def run_tick(deploy_status):
    """A separate process, run later: no session history, just the stored
    record and the current state. This is the part PM-Bench calls deciding
    whether a deferred task is due while other activity continues."""
    state = {"deploy_status": deploy_status, "tests_failed": 0}
    print(f"=== TICK (new process) ===")
    print("current state:", state)
    rec = load_record()
    if rec["status"] != "pending":
        print(f"trigger field '{rec['trigger_state_key']}' already handled (status={rec['status']}) -> skip, no re-fire")
        return
    observed = state.get(rec["trigger_state_key"])
    trigger_matches = (
        isinstance(observed, str)
        and isinstance(rec["trigger_value"], str)
        and observed.strip().lower() == rec["trigger_value"].strip().lower()
    ) or observed == rec["trigger_value"]
    if not trigger_matches:
        print(f"trigger not met: {rec['trigger_state_key']}={observed!r}, waiting for {rec['trigger_value']!r} -> nothing happens")
        return
    print(f"trigger met: {rec['trigger_state_key']}={observed!r} -> firing stored action")
    act_prompt = (
        "You previously agreed to this deferred task:\n"
        f"  label: {rec['label']}\n"
        f"  action to take: {rec['action_text']}\n\n"
        f"The trigger has now fired. Current state: {json.dumps(state)}\n\n"
        "Carry out the action using only this information. Be brief."
    )
    print("\n--- fresh prompt sent to the model (no session history included) ---")
    print(act_prompt)
    reply = chat([{"role": "user", "content": act_prompt}])
    print("\n--- model output ---")
    print(reply)
    rec["status"] = "done"
    save_record(rec)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "session":
        run_session()
    elif args and args[0] == "tick" and len(args) == 2:
        run_tick(args[1])
    else:
        print(__doc__)
        sys.exit(1)
