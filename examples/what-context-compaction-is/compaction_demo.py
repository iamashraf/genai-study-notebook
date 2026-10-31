"""Compaction demo: plant 3 facts early in a ~25-turn chat, summarise to ~100 words
with llama3.1:8b, then answer follow-ups from (a) full history vs (b) summary only.
Run: uv run examples/what-context-compaction-is/compaction_demo.py"""
import json, urllib.request

MODEL = "llama3.1:8b"

def chat(messages):
    body = {"model": MODEL, "messages": messages, "stream": False,
            "options": {"temperature": 0}}
    req = urllib.request.Request("http://localhost:11434/api/chat", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=1800))["message"]["content"].strip()

# Planted facts: (question, keyword that must appear in a correct answer)
FACTS = [("What is the total budget for the project?", "48,500"),
         ("What is the hard deadline for launch?", "14 March"),
         ("What constraint applies to vendors?", "EU")]

TURNS = [
 ("Hi, I'm planning a company offsite for 60 people. Can you help me organise it?", "Happy to help. What are the main constraints?"),
 ("First, the total budget is $48,500 and we cannot exceed it.", "Understood: $48,500 maximum."),
 ("The offsite must happen before the hard deadline of 14 March, because the fiscal year closes then.", "Noted, everything must be done by 14 March."),
 ("One more rule: legal says we may only use vendors based inside the EU.", "Got it, EU-based vendors only."),
 ("Let's talk venues. I like the idea of a lakeside hotel.", "Lakeside hotels are popular. Do you want conference rooms on site?"),
 ("Yes, one big room and two breakout rooms.", "A hotel with three meeting spaces would fit."),
 ("Should we do dinner at the hotel or somewhere else?", "Hotel dinner is simpler to coordinate; an outside restaurant is more memorable."),
 ("Let's keep dinner at the hotel on night one.", "Fine. Hotel dinner on night one."),
 ("What about transport from the airport?", "A shared shuttle is cheapest for 60 people."),
 ("Shuttle sounds fine. Two trips should do it.", "Two shuttle trips, noted."),
 ("Now the agenda. I want a morning keynote.", "A 9:30 keynote works well after breakfast."),
 ("Then workshops in the afternoon.", "Two parallel workshop tracks would use the breakout rooms."),
 ("Good. How about a team activity on day two?", "A guided hike or a cooking class are both common choices."),
 ("Cooking class sounds fun.", "Cooking class on day two, then."),
 ("Should we get branded notebooks for everyone?", "Branded notebooks are inexpensive and well received."),
 ("Yes, but keep them simple.", "Simple branded notebooks, noted."),
 ("What dietary needs should I check?", "Ask attendees about vegetarian, vegan, halal, kosher and allergy needs."),
 ("I'll send a survey for that.", "A short form with checkboxes works best."),
 ("Can you suggest a name for the offsite?", "How about 'Lakeside Reset'?"),
 ("I like it. Let's use that.", "Great, 'Lakeside Reset' it is."),
 ("What should the welcome email say?", "Greeting, dates, location, travel details and a link to the survey."),
 ("Keep it friendly and short.", "Will do, under 120 words."),
 ("Last thing: how do we collect RSVPs?", "A simple form with a reply-by date."),
 ("Okay, RSVP form it is.", "RSVP form, noted."),
]

def history():
    msgs = []
    for u, a in TURNS:
        msgs += [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
    return msgs

def ask(context, q):
    return chat(context + [{"role": "user", "content": q + " Answer in one short sentence."}])

full = history()
print(f"Conversation: {len(TURNS)} turns, {len(' '.join(m['content'] for m in full).split())} words\n")
print("== (a) FULL HISTORY ==")
for q, kw in FACTS:
    a = ask(full, q); print(f"[{'OK ' if kw in a else 'MISS'}] {q} -> {a}")

WORDINGS = [
 "Summarise this conversation in about 100 words so a colleague can continue the work.",
 "Compress the conversation above into a handoff note of roughly 100 words.",
 "Write a short summary (around 100 words) of what has been decided so far.",
]
transcript = "\n".join(f"{m['role']}: {m['content']}" for m in full)
for i, w in enumerate(WORDINGS, 1):
    s = chat([{"role": "user", "content": f"{transcript}\n\n{w}"}])
    print(f"\n== (b) SUMMARY #{i} ({len(s.split())} words) ==\n{s}\n")
    ctx = [{"role": "user", "content": "Summary of our earlier conversation:\n" + s}]
    kept = 0
    for q, kw in FACTS:
        a = ask(ctx, q); ok = kw in a; kept += ok
        print(f"[{'OK ' if ok else 'MISS'}] {q} -> {a}")
    print(f"facts in summary text: {[kw for _, kw in FACTS if kw in s]}  | answered correctly: {kept}/3")
