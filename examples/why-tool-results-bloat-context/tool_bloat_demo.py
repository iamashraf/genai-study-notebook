"""Backs the claims in posts/why-tool-results-bloat-context.md.
Run with: uv run examples/why-tool-results-bloat-context/tool_bloat_demo.py

Simulates a 10-step agent run (generated data, fixed seed) where every tool
returns either its full raw dump or only the fields the question needs.
Counts real tokens (tiktoken o200k_base) of everything piled up in context
after each step and prints them. Needs no model and no network.
Pass --svg to also rewrite assets/why-tool-results-bloat-context.svg.
"""
import json, random, sys
import tiktoken


enc = tiktoken.get_encoding("o200k_base")
tok = lambda s: len(enc.encode(s))
rnd = random.Random(7)

QUESTION = "Which deploy caused the checkout errors, and who authored it?"
NEEDLE = dict(id="d-4812", author="priya.n", service="checkout", time="14:07")
SERVICES = ["checkout", "search", "auth", "email", "billing", "catalog"]
PEOPLE = ["priya.n", "tom.k", "lena.v", "omar.s", "jia.w", "ravi.p"]


def deploys():
    out = []
    for i in range(80):
        d = dict(id=f"d-{4740 + i}", service=rnd.choice(SERVICES), author=rnd.choice(PEOPLE),
                 time=f"{9 + i // 10:02d}:{rnd.randint(0, 59):02d}", status="success",
                 commit=f"{rnd.getrandbits(160):040x}", message="Routine change " + "x" * rnd.randint(20, 80),
                 host=f"build-{rnd.randint(1, 30)}.internal", duration_s=rnd.randint(40, 600),
                 artifacts=[f"s3://builds/{rnd.getrandbits(48):x}/app.tar.gz"])
        out.append(d)
    out[72] = dict(out[72], **NEEDLE, message="Bump payment client timeout config")
    return out


def logs(n=150):
    out = []
    for i in range(n):
        lvl = rnd.choice(["INFO"] * 8 + ["WARN"])
        out.append(dict(ts=f"14:{rnd.randint(0, 59):02d}:{rnd.randint(0, 59):02d}", level=lvl,
                        service=rnd.choice(SERVICES), request_id=f"{rnd.getrandbits(64):016x}",
                        msg="request handled", headers={"user-agent": "Mozilla/5.0 " * 3, "accept": "*/*"}))
    for i in range(12):
        out.append(dict(ts=f"14:{12 + i}:00", level="ERROR", service="checkout", request_id=f"{rnd.getrandbits(64):016x}",
                        msg="PaymentTimeout after 30s calling payments-api",
                        trace="Traceback (most recent call last):\n" + "\n".join(f'  File "/srv/app/mod{j}.py", line {rnd.randint(1, 900)}, in handler' for j in range(12))))
    return out


def rows(n, extra):
    return [dict(id=i, region=rnd.choice(["us", "eu", "ap"]), created=f"2026-10-{rnd.randint(1, 30):02d}",
                 payload=extra + " " + "lorem ipsum " * rnd.randint(8, 20)) for i in range(n)]


D, L = deploys(), logs()
# (tool call, raw result, trimmed result) per step
STEPS = [
    ("list_deploys(last_3h)", D, [dict(id=d["id"], service=d["service"], author=d["author"], time=d["time"]) for d in D if d["time"] >= "14:00"]),
    ("search_logs(level=any)", L, {"error_count": 12, "service": "checkout", "first_error": "14:12:00", "msg": "PaymentTimeout after 30s calling payments-api"}),
    ("get_error_rate(checkout)", rows(60, "metric"), {"before_14:10": "0.2%", "after_14:10": "31%"}),
    ("get_deploy_detail(d-4812)", dict(D[72], diff="\n".join(f"+ line {i} of config change" for i in range(120))), dict(id="d-4812", author="priya.n", message=D[72]["message"], time="14:07")),
    ("read_file(payments_client.py)", {"path": "payments_client.py", "content": "\n".join(f"# line {i}: client code" for i in range(300))}, "TIMEOUT_S = 30  # changed from 5 in d-4812 (line 41)"),
    ("db_query(orders failed)", rows(70, "order"), {"failed_orders": 214, "window": "14:12-14:40"}),
    ("get_oncall(checkout)", rows(40, "oncall"), {"oncall": "omar.s"}),
    ("search_wiki(payment timeout)", rows(50, "wiki"), {"runbook": "Timeouts above 10s exhaust the worker pool"}),
    ("list_alerts(14:00-15:00)", rows(55, "alert"), {"alerts": ["checkout-latency", "checkout-errors"]}),
    ("get_rollback_options(d-4812)", rows(45, "rollback"), {"previous_good": "d-4811"}),
]

def ctx(strategy, k):
    return "\n\n".join(f"TOOL CALL: {c}\nRESULT: {json.dumps(raw if strategy == 'full' else trim)}" for c, raw, trim in STEPS[:k])

full_pts, trim_pts = [], []
for k in range(1, 11):
    f, t = tok(ctx("full", k)), tok(ctx("trim", k))
    full_pts.append(f); trim_pts.append(t)
    print(f"step {k:2d}  {STEPS[k-1][0]:32s} full={f:6d}  trimmed={t:5d}")
print(f"\nafter 10 steps: full={full_pts[-1]} tokens, trimmed={trim_pts[-1]} tokens, ratio {full_pts[-1]/trim_pts[-1]:.0f}x")
print("largest single raw result:", max(tok(json.dumps(r)) for _, r, _ in STEPS), "tokens")


if "--svg" in sys.argv:
    sys.path.insert(0, "scripts")
    import svgdiagram as S
    # diagram
    w, h = 560, 280
    pl, pr, pt, pb = 64, w - 90, 56, h - 50
    ymax = max(full_pts)
    X = lambda i: pl + (pr - pl) * i / 9
    Y = lambda v: pb - (pb - pt) * v / ymax
    p = [S.header(w, h), S._text_lines(w / 2, 22, ["Tokens piled up in context, step by step (10-step agent run)"], size=13.5, weight="700")]
    for g in range(1, 5):
        gy = pb - (pb - pt) * g / 4
        p.append(f'<line x1="{pl}" y1="{gy:.1f}" x2="{pr}" y2="{gy:.1f}" stroke="{S.GRIDLINE}"/>')
        p.append(S._text_lines(pl - 6, gy + 3, [f"{ymax*g/4/1000:.0f}k"], size=9.5, color=S.MUTED, anchor="end"))
    p.append(f'<line x1="{pl}" y1="{pb}" x2="{pr}" y2="{pb}" stroke="{S.BASELINE}"/>')
    for i in range(10):
        p.append(S._text_lines(X(i), pb + 16, [str(i + 1)], size=9.5, color=S.MUTED))
    p.append(S._text_lines((pl + pr) / 2, pb + 36, ["tool-call step"], size=10, color=S.MUTED))
    for pts, col, sw in ((full_pts, S.MUTED, 2), (trim_pts, S.C1, 2.5)):
        d = "M " + " L ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(pts))
        p.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
        p.append(f'<circle cx="{X(9):.1f}" cy="{Y(pts[-1]):.1f}" r="4" fill="{col}"/>')
    p.append(S._text_lines(X(9) + 8, Y(full_pts[-1]) - 8, [f"{full_pts[-1]:,}"], size=10.5, color=S.INK, weight="700", anchor="start", family=S.MONO))
    p.append(S._text_lines(X(9) + 8, Y(full_pts[-1]) + 6, ["raw dumps"], size=10, color=S.SUBINK, anchor="start"))
    p.append(S._text_lines(X(9) + 8, Y(trim_pts[-1]) - 10, [f"{trim_pts[-1]:,}"], size=10.5, color=S.C1, weight="700", anchor="start", family=S.MONO))
    p.append(S._text_lines(X(9) + 8, Y(trim_pts[-1]) + 4, ["trimmed"], size=10, color=S.C1, anchor="start"))
    p.append(S.FOOTER)
    open("assets/why-tool-results-bloat-context.svg", "w").write("\n".join(p))
