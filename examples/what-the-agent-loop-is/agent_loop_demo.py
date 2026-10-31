"""Backs the claims in posts/what-the-agent-loop-is.md.
Run with: uv run examples/what-the-agent-loop-is/agent_loop_demo.py

Requires a local Ollama server (http://localhost:11434) with llama3.1:8b pulled.
A complete agent loop: ask the model for a JSON action, run the tool,
append the result to the message list, repeat until it says "final".
"""
import json, urllib.request, tiktoken

ORDERS = {"A-1001": {"item": "desk lamp", "unit_price": 24.50, "qty": 3}}
TOOLS = {
    "lookup_order": lambda a: ORDERS.get(a["order_id"], "no such order"),
    "calculator": lambda a: eval(a["expression"], {"__builtins__": {}}),  # demo only
}
SYSTEM = (
    "You are an agent. Reply with ONE JSON object per turn, nothing else.\n"
    'To use a tool: {"thought": "...", "action": "lookup_order", "args": {"order_id": "A-1001"}}\n'
    'or {"thought": "...", "action": "calculator", "args": {"expression": "2*3"}}\n'
    'When done: {"thought": "...", "action": "final", "args": {"answer": "..."}}\n'
    "Never do arithmetic yourself; use the calculator. Tool results arrive as 'Observation:' messages."
)
enc = tiktoken.get_encoding("cl100k_base")
size = lambda msgs: sum(len(enc.encode(m["content"])) for m in msgs)

def ask(messages):
    body = {"model": "llama3.1:8b", "messages": messages, "stream": False,
            "format": "json", "options": {"temperature": 0}}
    req = urllib.request.Request("http://localhost:11434/api/chat", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["message"]["content"]

messages = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "What is the total cost of order A-1001, with 8% tax added?"}]
print(f"start: context = {size(messages)} tokens")
for step in range(1, 8):
    reply = ask(messages)
    messages.append({"role": "assistant", "content": reply})
    act = json.loads(reply)
    print(f"\n--- step {step} ---\nMODEL : {reply}")
    if act["action"] == "final":
        print(f"context after step {step}: {size(messages)} tokens"); break
    try:
        obs = TOOLS[act["action"]](act["args"])
    except Exception as e:
        obs = f"error: {e}"
    print(f"TOOL  : {obs}")
    messages.append({"role": "user", "content": f"Observation: {obs}"})
    print(f"context after step {step}: {size(messages)} tokens")
