import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from svgdiagram import render_flow, NEUTRAL_FILL

W, H = 880, 460
nodes = {
    "semantic": {"x": 150, "y": 70, "w": 150, "text": "Semantic Memory"},
    "procedural": {"x": 150, "y": 225, "w": 150, "text": "Procedural Memory"},
    "episodic": {"x": 150, "y": 380, "w": 150, "text": "Episodic Memory"},
    "wm": {"x": 450, "y": 225, "shape": "circle", "r": 60, "text": "Working Memory"},
    "action": {"x": 750, "y": 225, "w": 130, "text": "Action"},
}
edges = [
    ("semantic", "wm", "retrieve"),
    ("episodic", "wm", "retrieve"),
    ("procedural", "wm", "retrieve"),
    ("wm", "action", "execute"),
    ("action", "episodic", "learn"),
]
svg = render_flow(nodes, edges, W, H)
out = os.path.join(os.path.dirname(__file__), '..', '..', 'assets',
                    'what-coala-is-and-why-agent-memory-splits-this-way.svg')
open(out, 'w').write(svg)
print("wrote", out)
