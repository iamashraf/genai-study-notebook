import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from svgdiagram import render_card

svg = render_card("Procedural Memory", [
    ("WHAT IT IS", "A stored routine or skill an agent reuses instead of re-deriving it. CoALA names it "
                   "procedural memory: implicit knowledge in the LLM's weights, plus explicit knowledge "
                   "written into the agent's code [1]."),
    ("WHY IT MATTERS", "Without it, every task is solved from zero. With it, a known method is retrieved "
                       "and reused, the way Voyager retrieves a code-based skill instead of rewriting it [2]."),
    ("WHERE IT LIVES", "Outside the context window, in a skill library: a vector database keyed by the "
                       "embedding of what the skill does, valued by the skill itself [2]."),
    ("EXAMPLE", "A venue-finding method (filter by area, by headcount, by availability, sort by price) "
               "is retrieved by embedding similarity for a new, different venue request and reused instead "
               "of re-derived."),
])
out = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'what-procedural-memory-is-in-an-agent.svg')
open(out, 'w').write(svg)
print("wrote", out)
