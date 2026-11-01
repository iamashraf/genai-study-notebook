import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from svgdiagram import render_card

svg = render_card("Prospective Memory", [
    ("WHAT IT IS", "A stored intention: a trigger condition plus an action, "
                    "not currently in the context window."),
    ("HOW IT DIFFERS", "Not a fact (semantic), not a past event (episodic), "
                        "not a how-to (procedural). It points at the future."),
    ("WHERE IT LIVES", "An external record outside the session, checked "
                        "later by a fresh process, like a cron tick."),
    ("EXAMPLE", "\"Once the deploy finishes, tell me the result\" is saved, "
                "then fired only when deploy_status becomes finished."),
])
out = os.path.join(os.path.dirname(__file__), '..', '..', 'assets',
                    'what-prospective-memory-is-in-an-agent.svg')
open(out, 'w').write(svg)
print("wrote", out)
