import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from svgdiagram import render_card

svg = render_card("Episodic Memory", [
    ("WHAT IT IS", "A record of one specific past experience: what the agent tried, "
                    "when, and whether it worked. Not a general fact, and not the "
                    "current context window."),
    ("WHY IT MATTERS", "Lets the agent say \"last time I tried X, it failed because "
                        "Y\" and act on that instead of repeating the mistake."),
    ("HOW IT'S RETRIEVED", "Each stored episode gets a recency score, an importance "
                            "score, and a relevance score against the current "
                            "situation; the three combine into one retrieval score."),
    ("EXAMPLE", "Booking a Saturday venue: an old episode about a venue closed for "
                "renovation outranks a more recent Wi-Fi outage, because it scores "
                "higher on importance and relevance."),
])
out = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'what-episodic-memory-is-in-an-agent.svg')
open(out, 'w').write(svg)
print("wrote", out)
