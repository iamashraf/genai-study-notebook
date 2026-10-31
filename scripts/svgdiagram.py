"""Small, dependency-free SVG diagram primitives for the study-notebook's static assets.
Palette, mark specs, and color-assignment rules follow the project's dataviz skill
(references/palette.md, marks-and-anatomy.md, anti-patterns.md) rather than ad hoc choices.
"""
import html
import math

# -- chrome & ink (palette.md "Chart chrome & ink", light mode) --
BG = "#fcfcfb"
INK = "#0b0b0b"
SUBINK = "#52514e"
MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
BORDER = "#d8d6cd"
NEUTRAL_FILL = "#f3f2ef"
MUTED_FILL = "#cdccc3"

# -- categorical, fixed order (palette.md "Categorical palette", light) --
C1 = "#2a78d6"  # blue
C2 = "#eb6834"  # orange
C3 = "#1baf7a"  # aqua
C4 = "#eda100"  # yellow
C5 = "#e87ba4"  # magenta
C6 = "#008300"  # green
C7 = "#6250d6"  # violet
C8 = "#e34948"  # red

# -- status, reserved (palette.md "Status palette") --
GOOD = "#0ca30c"
WARNING = "#fab219"
SERIOUS = "#ec835a"
CRITICAL = "#d03b3b"

# -- sequential blue ramp (palette.md "Sequential hue") --
SEQ_250 = "#86b6ef"
SEQ_450 = "#2a78d6"
SEQ_650 = "#104281"

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"


def esc(s):
    return html.escape(str(s))


def _wrap(text, max_chars):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def _text_lines(x, y, lines, size=13, color=INK, weight="400", anchor="middle", family=FONT, line_h=16):
    out = []
    start_y = y - (len(lines) - 1) * line_h / 2
    for i, line in enumerate(lines):
        out.append(
            f'<text x="{x}" y="{start_y + i*line_h:.1f}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}" font-family="{family}">{esc(line)}</text>'
        )
    return "\n".join(out)


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" font-family="{FONT}">\n'
        f'<rect width="{w}" height="{h}" fill="{BG}"/>\n'
    )


FOOTER = "</svg>"

# ---------- A. flow / graph (boxes or circles + arrows) ----------
# Neutral chrome throughout -- an accent is used only when a node is
# semantically good/bad (status), never as decoration per-node.

def _prep_node(n):
    if n.get("shape") == "circle":
        r = n.get("r", 34)
        lines = _wrap(n["text"], max(8, int(r * 0.34)))
        n["_lines"], n["_r"] = lines, r
        return n
    bw = n.get("w", 140)
    max_chars = max(10, int((bw - 24) / 6.6))
    lines = _wrap(n["text"], max_chars)
    line_h = 17
    bh = max(n.get("h", 0), len(lines) * line_h + 26)
    n["_lines"], n["_bw"], n["_bh"] = lines, bw, bh
    return n


def _anchor(n, ang):
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    if n.get("shape") == "circle":
        r = n["_r"]
        return n["x"] + cos_a * r, n["y"] + sin_a * r
    hw, hh = n["_bw"] / 2, n["_bh"] / 2
    t_candidates = []
    if abs(cos_a) > 1e-6:
        t_candidates.append(hw / abs(cos_a))
    if abs(sin_a) > 1e-6:
        t_candidates.append(hh / abs(sin_a))
    t = min(t_candidates) if t_candidates else 0
    return n["x"] + cos_a * t, n["y"] + sin_a * t


def render_flow(nodes, edges, w, h):
    """nodes: {id: {x,y,w?,h?,text,fill?,color?,shape?('box'|'circle')}}
       edges: [(from,to,label?,color?)]
       fill defaults to a neutral surface; pass a status color only when a node
       is itself the good/bad outcome, never as per-node decoration."""
    for n in nodes.values():
        _prep_node(n)

    parts = [header(w, h)]
    parts.append(
        f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        f'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>'
    )
    for (a, b, *rest) in edges:
        label = rest[0] if len(rest) > 0 else None
        color = rest[1] if len(rest) > 1 else MUTED
        na, nb = nodes[a], nodes[b]
        x1, y1 = na["x"], na["y"]
        x2, y2 = nb["x"], nb["y"]
        ang = math.atan2(y2 - y1, x2 - x1)
        sx, sy = _anchor(na, ang)
        ex, ey = _anchor(nb, ang + math.pi)
        gap = 6
        seg_ang = math.atan2(ey - sy, ex - sx)
        sx += math.cos(seg_ang) * gap
        sy += math.sin(seg_ang) * gap
        ex -= math.cos(seg_ang) * gap
        ey -= math.sin(seg_ang) * gap
        parts.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="1.6" marker-end="url(#arrow)"/>')
        if label:
            mx, my = (sx + ex) / 2, (sy + ey) / 2 - 8
            parts.append(_text_lines(mx, my, [label], size=11, color=color, weight="600"))

    for nid, n in nodes.items():
        fill = n.get("fill", NEUTRAL_FILL)
        textcolor = n.get("color", INK)
        if n.get("shape") == "circle":
            parts.append(f'<circle cx="{n["x"]}" cy="{n["y"]}" r="{n["_r"]}" fill="{fill}" stroke="{BORDER}" stroke-width="1.2"/>')
            parts.append(_text_lines(n["x"], n["y"], n["_lines"], size=11.5, color=textcolor, weight="600"))
        else:
            bw, bh = n["_bw"], n["_bh"]
            x, y = n["x"] - bw / 2, n["y"] - bh / 2
            parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="8" fill="{fill}" stroke="{BORDER}" stroke-width="1.2"/>')
            parts.append(_text_lines(n["x"], n["y"], n["_lines"], size=12, color=textcolor, weight="600"))
    parts.append(FOOTER)
    return "\n".join(parts)


# ---------- B. bar chart (thin marks, hairline grid, status/categorical color by rule) ----------

def render_bars(title, groups, legend=None, log_scale=False, value_fmt="{:.4f}", unit=""):
    """groups: [{"label": str, "bars": [{"name","value","color"}]}]
       legend: optional [(label,color)] -- pass only for genuine multi-series charts.
       Bars are capped at 24px with 4px rounded data-ends, square at the baseline,
       per the project's mark spec -- never full-width saturated blocks. Each bar
       gets a wider label "slot" than its own drawn width, so long names wrap
       without colliding with the neighboring bar's label."""
    bar_w = 22
    group_gap = 40
    name_line_h, group_line_h = 12, 14
    side_margin = 50
    min_slot_w = 88  # label column width, independent of the thin bar's drawn width

    max_bars = max(len(g["bars"]) for g in groups)
    slot_w = max(bar_w + 10, min_slot_w)
    group_w = max_bars * slot_w
    bars_w = side_margin * 2 + len(groups) * group_w + (len(groups) - 1) * group_gap

    title_w = len(title) * 7.6 + 50
    w = max(bars_w, title_w)
    # if we widened for the title, spread the extra width into side margins so bars stay centered
    extra = max(0, w - bars_w)
    side_margin += extra / 2

    prepared = []
    max_name_lines, max_group_lines = 1, 1
    for g in groups:
        name_max_chars = max(10, int((slot_w - 10) / 5.0))
        per_bar = []
        for b in g["bars"]:
            lines = _wrap(b["name"], name_max_chars) if b.get("name") else []
            if lines:
                max_name_lines = max(max_name_lines, len(lines))
            per_bar.append((b, lines))
        glines = _wrap(g["label"], max(10, int(group_w / 6.0)))
        max_group_lines = max(max_group_lines, len(glines))
        prepared.append((g, per_bar, glines))

    plot_top = 76 if legend else 58
    plot_h = 180
    plot_bottom = plot_top + plot_h
    name_block_h = max_name_lines * name_line_h + 8
    group_y0 = plot_bottom + 18 + name_block_h + 8
    h = group_y0 + max_group_lines * group_line_h + 16

    parts = [header(w, h)]
    parts.append(_text_lines(w / 2, 24, [title], size=13.5, color=INK, weight="700"))

    if legend:
        lx = w / 2 - (len(legend) * 90) / 2
        for name, color in legend:
            parts.append(f'<rect x="{lx:.1f}" y="42" width="10" height="10" rx="2" fill="{color}"/>')
            parts.append(f'<text x="{lx+16:.1f}" y="51" font-size="10.5" fill="{SUBINK}" font-family="{FONT}">{esc(name)}</text>')
            lx += 90

    all_vals = [b["value"] for g in groups for b in g["bars"]]
    vmax = max(all_vals) if all_vals else 1

    def scale(v):
        if log_scale:
            v = max(v, 1)
            return math.log10(v) / math.log10(vmax) if vmax > 1 else 0
        return v / vmax if vmax else 0

    # hairline gridlines (recessive), 4 steps
    for i in range(1, 4):
        gy = plot_top + plot_h * (1 - i / 4)
        parts.append(f'<line x1="{side_margin-10:.1f}" y1="{gy:.1f}" x2="{w-side_margin+10:.1f}" y2="{gy:.1f}" stroke="{GRIDLINE}" stroke-width="1"/>')

    for gi, (g, per_bar, glines) in enumerate(prepared):
        gx = side_margin + gi * (group_w + group_gap)
        for bi, (b, lines) in enumerate(per_bar):
            slot_x = gx + bi * slot_w
            bx = slot_x + (slot_w - bar_w) / 2
            bh = max(plot_h * scale(b["value"]), 1.5)
            by = plot_bottom - bh
            color = b.get("color", C1)
            r = min(4, bh / 2)
            parts.append(
                f'<path d="M {bx:.1f},{plot_bottom} L {bx:.1f},{by+r:.1f} Q {bx:.1f},{by:.1f} {bx+r:.1f},{by:.1f} '
                f'L {bx+bar_w-r:.1f},{by:.1f} Q {bx+bar_w:.1f},{by:.1f} {bx+bar_w:.1f},{by+r:.1f} L {bx+bar_w:.1f},{plot_bottom} Z" fill="{color}"/>'
            )
            valtxt = value_fmt.format(b["value"]) + unit
            parts.append(_text_lines(slot_x + slot_w / 2, max(by - 10, plot_top - 18), [valtxt], size=10, color=INK, weight="700", family=MONO))
            name_y0 = plot_bottom + 18
            for li, line in enumerate(lines):
                parts.append(
                    f'<text x="{slot_x+slot_w/2:.1f}" y="{name_y0 + li*name_line_h:.1f}" font-size="9" fill="{MUTED}" '
                    f'text-anchor="middle" font-family="{FONT}">{esc(line)}</text>'
                )
        for li, line in enumerate(glines):
            parts.append(
                f'<text x="{gx+group_w/2:.1f}" y="{group_y0 + li*group_line_h:.1f}" font-size="10.5" fill="{SUBINK}" '
                f'font-weight="600" text-anchor="middle" font-family="{FONT}">{esc(line)}</text>'
            )

    parts.append(f'<line x1="{side_margin-10:.1f}" y1="{plot_bottom}" x2="{w-side_margin+10:.1f}" y2="{plot_bottom}" stroke="{BASELINE}" stroke-width="1"/>')
    parts.append(FOOTER)
    return "\n".join(parts)


# ---------- C. line / decay chart ----------

def render_line(title, points, w=460, h=230, color=C1, ylabel="", log_y=False):
    """points: [(x_label, y_value)]"""
    parts = [header(w, h)]
    parts.append(_text_lines(w / 2, 22, [title], size=13.5, color=INK, weight="700"))

    ys = [p[1] for p in points]
    ymax, ymin = max(ys), min(ys)
    plot_left, plot_right = 50, w - 26
    plot_top, plot_bottom = 44, h - 46
    n = len(points)

    for i in range(1, 4):
        gy = plot_top + (plot_bottom - plot_top) * i / 4
        parts.append(f'<line x1="{plot_left}" y1="{gy:.1f}" x2="{plot_right}" y2="{gy:.1f}" stroke="{GRIDLINE}" stroke-width="1"/>')

    def xpos(i):
        return plot_left + (plot_right - plot_left) * (i / max(n - 1, 1))

    def ypos(v):
        if log_y:
            v = max(v, 0.001)
            lo, hi = math.log10(max(ymin, 0.001)), math.log10(ymax)
            t = (math.log10(v) - lo) / (hi - lo) if hi > lo else 0
        else:
            t = (v - ymin) / (ymax - ymin) if ymax > ymin else 0
        return plot_bottom - (plot_bottom - plot_top) * t

    path_pts = [(xpos(i), ypos(p[1])) for i, p in enumerate(points)]
    path_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in path_pts)
    area_d = path_d + f" L {path_pts[-1][0]:.1f},{plot_bottom} L {path_pts[0][0]:.1f},{plot_bottom} Z"
    parts.append(f'<path d="{area_d}" fill="{color}" opacity="0.08"/>')
    parts.append(f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="2"/>')

    for i, (x, y) in enumerate(path_pts):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{BG}" stroke="{color}" stroke-width="2"/>')
        label, val = points[i]
        parts.append(_text_lines(x, plot_bottom + 18, [label], size=9.5, color=MUTED))
        parts.append(_text_lines(x, y - 12, [f"{val:g}"], size=10, color=INK, weight="700", family=MONO))

    parts.append(f'<line x1="{plot_left}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" stroke="{BASELINE}" stroke-width="1"/>')
    if ylabel:
        parts.append(f'<text x="14" y="{(plot_top+plot_bottom)/2:.0f}" font-size="9.5" fill="{MUTED}" '
                      f'text-anchor="middle" transform="rotate(-90 14 {(plot_top+plot_bottom)/2:.0f})" font-family="{FONT}">{esc(ylabel)}</text>')
    parts.append(FOOTER)
    return "\n".join(parts)


# ---------- D. highlighted text chunks ----------

def render_text_chunks(title, rows, w=620):
    """rows: [{"label": str, "segments": [(text, color)]}] -- one row per scheme being compared"""
    row_h = 54
    h = 60 + row_h * len(rows) + 20
    parts = [header(w, h)]
    parts.append(_text_lines(w / 2, 22, [title], size=13.5, color=INK, weight="700"))

    y = 54
    for row in rows:
        parts.append(_text_lines(16, y + 14, [row["label"]], size=10, color=SUBINK, weight="700", anchor="start"))
        x = 16
        bx_y = y + 22
        for text, color in row["segments"]:
            tw = 7.2 * len(text) + 16
            parts.append(f'<rect x="{x}" y="{bx_y}" width="{tw:.1f}" height="24" rx="5" fill="{color}"/>')
            parts.append(_text_lines(x + tw / 2, bx_y + 16, [text], size=11, color="#ffffff", weight="700", family=MONO))
            x += tw + 6
        y += row_h
    parts.append(FOOTER)
    return "\n".join(parts)


# ---------- E. proximity (distance-as-layout) ----------

def render_proximity(title, center, items, w=480, h=190):
    """items: [(label, similarity_0to1, color)] -- higher similarity drawn closer to center"""
    parts = [header(w, h)]
    parts.append(_text_lines(w / 2, 22, [title], size=13.5, color=INK, weight="700"))
    cx, cy = 66, h / 2 + 8
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="28" fill="{NEUTRAL_FILL}" stroke="{BORDER}" stroke-width="1.2"/>')
    parts.append(_text_lines(cx, cy, [center], size=11.5, color=INK, weight="700"))

    max_dist = w - 150
    for label, sim, color in items:
        dist = 56 + (1 - sim) * max_dist
        x = cx + dist
        parts.append(f'<line x1="{cx+30}" y1="{cy}" x2="{x-24}" y2="{cy}" stroke="{color}" stroke-width="1.6" stroke-dasharray="3 4"/>')
        parts.append(f'<circle cx="{x}" cy="{cy}" r="24" fill="{color}" opacity="0.14" stroke="{color}" stroke-width="1.4"/>')
        parts.append(_text_lines(x, cy - 2, [label], size=11, color=INK, weight="700"))
        parts.append(_text_lines(x, cy + 14, [f"{sim:.3f}"], size=9.5, color=SUBINK, weight="700", family=MONO))
    parts.append(FOOTER)
    return "\n".join(parts)
