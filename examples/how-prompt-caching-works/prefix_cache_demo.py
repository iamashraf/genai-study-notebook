"""Does Ollama reuse already-processed prompt tokens when a prompt starts the same way?
Same long handout each time; vary either the question at the END (a) or the first line (b)."""
import json, statistics as st, urllib.request

MODEL = "llama3.1:8b"
FACTS = [f"Rule {i}: Locker {100+i} belongs to team {chr(65+i%26)}{i}, and its code changes every {2+i%7} days."
         for i in range(1, 121)]
HANDOUT = "\n".join(FACTS)
QUESTIONS = ["Who owns locker 105?", "How often does locker 110 change?", "Which team has locker 120?",
             "What is rule 7 about?", "Who owns locker 133?", "How often does locker 150 change?"]


def ask(prompt):
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False, "keep_alive": "10m",
                       "options": {"temperature": 0, "num_predict": 8, "num_ctx": 4096}}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", body, {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=600))
    return r["prompt_eval_count"], r["prompt_eval_duration"] / 1e6, r["total_duration"] / 1e6


def show(label, rows):
    print(f"\n{label}")
    for i, (n, pe, tot) in enumerate(rows, 1):
        print(f"  run {i}: prompt_eval_count={n:5d}  prompt_eval={pe:8.1f} ms  total={tot:8.1f} ms")
    print(f"  median: prompt_eval_count={st.median(r[0] for r in rows):.0f}  "
          f"prompt_eval={st.median(r[1] for r in rows):.1f} ms  total={st.median(r[2] for r in rows):.1f} ms")


def prompt(first_line, question):
    return f"{first_line}\n{HANDOUT}\n\nQuestion: {question}\nAnswer briefly."


ask("hi")  # load the model so load time doesn't pollute the numbers
base = "You are a locker-room assistant. Answer only from the handout."
cold = ask(prompt(base, "Warm-up question?"))
print(f"cold first call (handout never seen): prompt_eval_count={cold[0]}  prompt_eval={cold[1]:.1f} ms  total={cold[2]:.1f} ms")

show("(a) same first line + same handout, different question at the end",
     [ask(prompt(base, q)) for q in QUESTIONS])
show("(b) first line changed every call (handout text identical)",
     [ask(prompt(f"{base} Session #{i}.", q)) for i, q in enumerate(QUESTIONS, 1)])
