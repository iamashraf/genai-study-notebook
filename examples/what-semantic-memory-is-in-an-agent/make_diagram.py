import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from svgdiagram import render_card

svg = render_card("Semantic Memory", [
    ("WHAT IT IS", "Durable facts an agent has learned about a user or the world, "
                    "kept outside the context window."),
    ("HOW IT DIFFERS", "Not a past event (episodic) and not what's in the window "
                        "now (working) -- a fact stated cold, no trace of when it "
                        "was learned."),
    ("WHERE IT LIVES", "A fact store outside the context window: key-value pairs, "
                        "not a transcript. Read back in on demand, any session."),
    ("EXAMPLE", "Session 1: user mentions he's vegetarian, based in Toronto. "
                "Session 2 (new chat): agent answers correctly using only stored "
                "facts."),
], w=640)
out = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'what-semantic-memory-is-in-an-agent.svg')
open(out, 'w').write(svg)
print("wrote", out)
