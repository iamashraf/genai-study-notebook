import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from svgdiagram import render_flow, _text_lines, INK, BG

TITLE_H = 36
nodes = {
    "working":     {"x": 100, "y": 70 + TITLE_H,  "w": 150, "text": "Working: the current task, right now"},
    "semantic":    {"x": 270, "y": 70 + TITLE_H,  "w": 150, "text": "Semantic: a fact you just know"},
    "episodic":    {"x": 440, "y": 70 + TITLE_H,  "w": 150, "text": "Episodic: one specific past event"},
    "procedural":  {"x": 610, "y": 70 + TITLE_H,  "w": 150, "text": "Procedural: a routine you've internalized"},
    "retrieval":   {"x": 185, "y": 210 + TITLE_H, "w": 150, "text": "Retrieval: looked up when needed"},
    "parametric":  {"x": 355, "y": 210 + TITLE_H, "w": 150, "text": "Parametric: baked into training"},
    "prospective": {"x": 525, "y": 210 + TITLE_H, "w": 150, "text": "Prospective: a commitment for later"},
}
w, h = 710, 290 + TITLE_H
svg = render_flow(nodes, [], w=w, h=h)
title_svg = _text_lines(w / 2, 26, ["Seven Kinds of Agent Memory"], size=14.5, color=INK, weight="700")
marker = f'<rect width="{w}" height="{h}" fill="{BG}"/>'
assert marker in svg, "background rect marker not found -- render_flow's header() format changed"
svg = svg.replace(marker, marker + "\n" + title_svg)
out = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'what-kinds-of-memory-an-agent-has.svg')
open(out, 'w').write(svg)
print("wrote", out)
