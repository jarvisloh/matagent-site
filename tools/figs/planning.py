"""Planning figure: a timeline builder for CDTP's study designer (C20, C21, C59). CDTP 3.3 routes the run to 3.2
(documents) or 3.1 (request + records); the designer, a language model and the one dark panel, writes drafted steps
onto a Gantt lane, each with its suggested parameters (C58, assumed). Rule checks tick or strike each block in amber;
valid steps are numbered and their core-hours stack along the lane at 2,000 per week. With at least two valid steps
the design totals the core-hours (odometer) and the weeks; with fewer, PLAN's rule-based template (the dashed stamp).
CDTP 3.3 then scores FS on the finished plan, a gauge whose needle settles last (C45 as assessed resources and tools,
assumed; C52: only CDTP 3.3 carries FS). The SVG is the finished frame; the GSAP intro builds it from hidden states and
the loop clears and replays one pass. A step's tick or strike appears only after its check, the bars after the tick,
and the gauge only after the design is complete."""
from html import escape
import math

from figkit import Figure, curve, curve_d, f, hdr, icon, legend, note, svg

GAPS = ["Ag effect on *CO", "C–C coupling sites"]  # the gap list (illustrative)
PAGES = ["3", "7", "12"]  # the excerpts shown, by page (illustrative)
# drafted steps (illustrative): task, method, suggested parameters, gap, cited page, core-hours, failed rule
STEPS = [
    ("Relax Cu–Ag (111) slabs", "DFT · RPBE", "450 eV · k 4×4×1", GAPS[0], "3", 1200, None),
    ("*CO at top and bridge", "DFT · RPBE", "450 eV · 2 sites", GAPS[0], "7", 2400, None),
    ("Solvation of *CO", "implicit solvent", "ε = 78.4", GAPS[0], "19", 1600, "page"),
    ("C–C coupling barriers", "CI-NEB · RPBE", "5 images", GAPS[1], "12", 6000, None),
    ("Selectivity vs potential", "microkinetic model", "0 to −1.2 V", "product selectivity", "12", 400, "gap"),
    ("Interface dynamics", "AIMD · 10 ps", "300 K", GAPS[1], "7", 350000, "hours"),
]
WHY = {"page": "p. 19 is not among the excerpts", "gap": "gap not on the list",
       "hours": "core-hours outside 1–200,000"}
WHY_N = {"page": "dropped: p. 19 not shown", "gap": "dropped: gap not on the list",
         "hours": "dropped: over 200,000 core-h"}
PER_WEEK, LANE_MAX = 2000, 10000
FS = 64  # illustrative

# the rules, in the order the code applies them (C20, C59)
for _t, _m, _p, _g, _pg, _h, _bad in STEPS:
    _fail = ("gap" if _g not in GAPS else "page" if _pg not in PAGES else "hours" if not 1 <= _h <= 200000 else None)
    assert _fail == _bad, (_t, _fail, _bad)
VALID = [s for s in STEPS if s[6] is None]
CUM = [0]
for _s in VALID:
    CUM.append(CUM[-1] + _s[5])
TOTAL, WEEKS = CUM[-1], max(1, math.ceil(CUM[-1] / PER_WEEK))
assert len(VALID) >= 2 and 3 <= len(STEPS) <= 6 and TOTAL <= LANE_MAX


def _n(v):
    return f"{v:,}"


# pass timing (seconds from the pass start), shared by intro and loop; both variants run on one clock. One designer
# call returns the whole list, so every block types in first; only then do the rule checks take the steps in order.
TY0, TS = .45, .3  # first block typed, typing stagger
C0, CK = TY0 + 5 * TS + .65, .4  # first check (after the last block is typed), check pitch
T = {"decflow": C0 + 5 * CK + .2}
T["dec"] = T["decflow"] + .3
T["yes"] = T["dec"] + .15
T["design"] = T["yes"] + .25
T["odo"] = [T["design"] + .2 + .25 * k for k in range(len(VALID))]
T["weeks"] = T["odo"][-1] + .3
T["fsc"] = T["weeks"] + .15
T["needle"] = T["fsc"] + .25
T["fsv"] = T["needle"] + 1.0
NEEDLE_D = 1.3
PASS = T["needle"] + NEEDLE_D
T0_INTRO, HOLD = .9, .7
T0_LOOP = HOLD + .45
T_LOOP = round(T0_LOOP + PASS + .3, 2)
assert T0_INTRO + PASS <= 10 and T_LOOP <= 10, (T0_INTRO + PASS, T_LOOP)

LABEL = ("Study design timeline, CDTP. CDTP 3.3 runs CDTP 3.2 when documents are given, else CDTP 3.1. CDTP 3.1 plans "
         "from the research request and any database records PLAN found, citing no pages, and the language model names "
         "2–5 gaps; CDTP 3.2 plans from page-cited excerpts, up to 12,000 characters by default. The study designer, a "
         "language model (one call by default, up to six in an approved workflow), drafts 3–6 steps, each with a task, "
         "method, system, purpose, gap, evidence, core-hours and suggested parameters, all returned in one reply. Rule "
         "checks then take the steps in order and strike a step in amber when its task, method or purpose is missing, its gap is not on the list, it "
         "cites a page outside the excerpts shown, or its core-hours, the model's own estimate, fall outside "
         "1–200,000. Valid steps are numbered, and their core-hours stack along the lane at 2,000 core-hours per week. "
         "With at least two valid steps, the study design totals the core-hours and gives the timeline in weeks, "
         "rounded up; with fewer, with no language model, or when CDTP 3.2 has no cited evidence, the plan stays "
         "PLAN's rule-based template, labelled template with the reason, and a CDTP 3.1 run that found no records is "
         "marked partial. CDTP 3.3 then scores feasibility, FS, on the finished plan, the template included, assessing "
         "resources and tools: a model-assisted "
         "measure of the run's own output. The steps, core-hours and FS value are illustrative.")
LEGEND = [("okc", "passes every rule: numbered"), ("xc", "dropped: a rule failed"), ("flow", "core-hours, stacked"),
          ("dash", "route not taken here")]
LEGEND_N = [[("okc", "valid: numbered"), ("xc", "dropped")], [("flow", "core-hours, stacked")]]
RULES = ["task, method or purpose is missing", "its gap is not on the list",
         "a cited page was not among the excerpts", "core-hours are outside 1–200,000"]
RULES_N = ["task, method or purpose missing", "gap not on the list", "cited page not among excerpts",
           "core-hours outside 1–200,000"]
CW = {"wide": 7.68, "narrow": 8.04}  # Geist Mono advance per character at the sub size


def _flow(d, t, cls="cv f-planning-cv", arrow=True):
    """Connector plus its teal flow overlay (hidden in the static frame), which each pass runs at time t."""
    m = ' marker-end="url(#arr)"' if arrow else ""
    return f'<path class="{cls}" d="{d}"{m}/><path class="f-planning-flow" d="{d}" data-t="{t:.2f}" opacity="0"/>'


def _defs(pre):
    return (f'<defs><linearGradient id="{pre}-pnl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="f-planning-g0"/>'
            '<stop offset="1" class="f-planning-g1"/></linearGradient></defs>')


def _ok(cx, cy, cls="f-planning-ok", r=12):
    return (f'<g class="{cls}"><circle cx="{f(cx)}" cy="{f(cy)}" r="{r}"/>'
            f'<path d="M{f(cx - 5)},{f(cy + .5)} l3.5,3.5 l6.5,-7.5"/></g>')


def _x(cx, cy):
    return (f'<g class="f-planning-x"><circle cx="{f(cx)}" cy="{f(cy)}" r="12"/>'
            f'<path d="M{f(cx - 4.5)},{f(cy - 4.5)} l9,9 M{f(cx + 4.5)},{f(cy - 4.5)} l-9,9"/></g>')


def _chip(x, y, w, text):
    return (f'<g class="f-planning-chip"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="22" rx="6"/>'
            f'<text class="sub f-planning-ct" x="{f(x + w / 2)}" y="{f(y + 15.5)}" text-anchor="middle">{escape(text)}</text></g>')


def _row(i, step, x, y, w, h, lane, chk, wide, pre):
    """One drafted step: the block (typed in through a clip wipe), its check stamp, and its lane bar or the reason.
    lane = (x0, units per core-hour, bar y, bar height); chk = check-stamp centre."""
    task, method, params, gap, page, hours, bad = step
    cw = CW["wide" if wide else "narrow"]
    ok = bad is None
    k = VALID.index(step) if ok else None
    tx, rx = x + 14, x + w - 14
    l1, l2, l3, l4 = y + 24, y + 44, y + (62 if wide else 63), y + (80 if wide else 82)
    hrs = f"{_n(hours)} core-h"
    cid = f"{pre}-c{i}"
    P = [f'<g class="f-planning-row" data-ok="{1 if ok else 0}">'
         f'<clipPath id="{cid}"><rect class="f-planning-wipe" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" data-w="{f(w)}"/></clipPath>'
         f'<g class="card f-planning-blk"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="9"/>'
         f'<g clip-path="url(#{cid})">'
         f'<text class="ttl sm" x="{f(x + 40)}" y="{f(l1)}">{escape(task)}</text>'
         f'<text class="sub f-planning-ink" x="{f(tx)}" y="{f(l2)}">{escape(method)}</text>'
         f'<text class="sub" x="{f(tx)}" y="{f(l3)}">{escape(params)}</text>'
         f'<text class="sub" x="{f(rx)}" y="{f(l3)}" text-anchor="end">{escape(hrs)}</text>'
         f'<text class="sub" x="{f(tx)}" y="{f(l4)}">{escape(gap)}</text>'
         f'<text class="sub" x="{f(rx)}" y="{f(l4)}" text-anchor="end">p. {page}</text>'
         '</g>' + ("" if wide else "".join(
             f'<path class="f-planning-grid" d="M{f(lane[0] + j * PER_WEEK * lane[1])},{f(lane[2] - 4)} v{f(lane[3] + 8)}"/>'
             for j in range(LANE_MAX // PER_WEEK + 1))) + '</g>'
         f'<rect class="f-planning-caret" x="{f(x)}" y="{f(y + 8)}" width="2.5" height="{f(h - 16)}" opacity="0" data-w="{f(w - 4)}"/>']
    if ok:
        P.append(f'<g class="f-planning-num"><circle cx="{f(x + 22)}" cy="{f(l1 - 5)}" r="10.5"/>'
                 f'<text class="f-planning-nt" x="{f(x + 22)}" y="{f(l1 - .5)}" text-anchor="middle">{k + 1}</text></g>')
        P.append(_ok(*chk))
        x0, u, by, bh = lane
        bx = x0 + CUM[k] * u
        P.append(f'<rect class="f-planning-bar" x="{f(bx)}" y="{f(by)}" width="{f(hours * u)}" height="{f(bh)}" rx="3" '
                 f'data-x0="{f(bx)}"/>')
    else:
        # the failing field gets an amber underline, the block an amber dashed outline, the task a strike
        if bad == "page":
            ux, ul, uy = rx - len(f"p. {page}") * cw, len(f"p. {page}") * cw, l4
        elif bad == "gap":
            ux, ul, uy = tx, len(gap) * cw, l4
        else:
            ux, ul, uy = rx - len(hrs) * cw, len(hrs) * cw, l3
        P.append(f'<rect class="f-planning-badrect" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="9"/>'
                 f'<path class="f-planning-under" d="M{f(ux)},{f(uy + 4)} h{f(ul)}"/>'
                 f'<path class="f-planning-strike" d="M{f(x + 36)},{f(l1 - 5)} H{f(x + w - (14 if wide else 44))}"/>')
        P.append(_x(*chk))
        x0, u, by, bh = lane
        why = WHY[bad] if wide else WHY_N[bad]
        P.append(f'<text class="lbl amb f-planning-why" x="{f(x0 + (8 if wide else 0))}" y="{f(by + bh / 2 + 4.5)}">{escape(why)}</text>')
    return "".join(P) + "</g>"


def _odo(pre, x, y, pitch=40, clip_w=120, clip_h=36):
    """Odometer of the running total: values stacked below the shown one; the static frame shows the last."""
    vals = [_n(v) for v in CUM]
    n = len(vals)
    t = "".join(f'<text class="f-planning-big" x="{f(x)}" y="{f(y + (n - 1 - k) * pitch)}">{v}</text>'
                for k, v in enumerate(vals))
    return (f'<clipPath id="{pre}-odo"><rect x="{f(x - 2)}" y="{f(y - clip_h + 4)}" width="{f(clip_w)}" '
            f'height="{f(clip_h + 4)}"/></clipPath><g clip-path="url(#{pre}-odo)">'
            f'<g class="f-planning-odo" data-pitch="{pitch}" data-n="{n}">{t}</g></g>')


def _gauge(cx, cy, r):
    """FS gauge: track, ticks, 0 and 100; the value arc and the needle point at FS (illustrative)."""
    ang = FS * 1.8
    th = math.radians(180 - ang)
    ex, ey = cx + r * math.cos(th), cy - r * math.sin(th)
    nx, ny = cx + (r - 16) * math.cos(th), cy - (r - 16) * math.sin(th)
    P = [f'<g class="f-planning-gbg"><path class="f-planning-arc" d="M{f(cx - r)},{f(cy)} A{r},{r} 0 0 1 {f(cx + r)},{f(cy)}"/>']
    for v in range(0, 101, 10):
        a = math.radians(180 - v * 1.8)
        r1, r2 = r - 13, r - (21 if v % 50 == 0 else 17)
        P.append(f'<path class="f-planning-gt" d="M{f(cx + r1 * math.cos(a))},{f(cy - r1 * math.sin(a))} '
                 f'L{f(cx + r2 * math.cos(a))},{f(cy - r2 * math.sin(a))}"/>')
    P.append(f'<text class="sub" x="{f(cx - r)}" y="{f(cy + 22)}" text-anchor="middle">0</text>'
             f'<text class="sub" x="{f(cx + r)}" y="{f(cy + 22)}" text-anchor="middle">100</text></g>')
    P.append(f'<path class="f-planning-fsarc" d="M{f(cx - r)},{f(cy)} A{r},{r} 0 0 1 {f(ex)},{f(ey)}"/>'
             f'<path class="f-planning-needle" d="M{f(cx)},{f(cy)} L{f(nx)},{f(ny)}" data-a="{ang:.1f}" '
             f'data-o="{f(cx)} {f(cy)}"/><circle class="f-planning-hub" cx="{f(cx)}" cy="{f(cy)}" r="5"/>')
    return "".join(P)


def _stamp(x, y, w, h, lines, wide):
    """PLAN's rule-based template: the dashed amber fallback stamp, slightly rotated."""
    cx, cy = x + w / 2, y + h / 2
    P = [f'<g class="f-planning-stamp" transform="rotate(-3 {f(cx)} {f(cy)})">'
         f'<rect class="f-planning-st0" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
         f'<rect x="{f(x + 5)}" y="{f(y + 5)}" width="{f(w - 10)}" height="{f(h - 10)}" rx="7"/>'
         f'<text class="hdr f-planning-amb" x="{f(x + 20)}" y="{f(y + 30)}">RULE-BASED TEMPLATE</text>']
    yy = y + 54
    for cls, a, b in lines:
        P.append(f'<text class="{cls}" x="{f(x + 20)}" y="{f(yy)}">{escape(a)}</text>')
        if b:
            P.append(f'<text class="{cls}" x="{f(x + w - 20)}" y="{f(yy)}" text-anchor="end">{escape(b)}</text>')
        yy += 20
    return "".join(P) + "</g>"


def _panel(pre, x, y, w, h, wide):
    """The study designer, the figure's one dark panel; h=None fits the panel to its content."""
    P = [icon("plan", x + 16, y + 17, "ic f-planning-pic"),
         f'<text class="f-planning-lmt" x="{f(x + 42)}" y="{f(y + 32)}">Language model</text>']
    if wide:
        subs = [("study designer", None), ("drafts 3–6 steps", None), ("1 call by default", None),
                ("≤ 6 calls if approved", None)]
        fields = [("task · method", None), ("system · purpose", None), ("gap · evidence", None),
                  ("core-hours", None), ("suggested parameters", None)]
    else:
        subs = [("study designer", "drafts 3–6 steps"), ("1 call by default", "≤ 6 if approved")]
        fields = [("task · method", "system · purpose"), ("gap · evidence", "core-hours"),
                  ("suggested parameters", None)]
    yy = y + 58
    for a, b in subs:
        P.append(f'<text class="sub f-planning-on" x="{f(x + 16)}" y="{f(yy)}">{escape(a)}</text>')
        if b:
            P.append(f'<text class="sub f-planning-on" x="{f(x + w - 16)}" y="{f(yy)}" text-anchor="end">{escape(b)}</text>')
        yy += 20
    dy = yy - 2
    dh = 30 + 20 * len(fields)
    P.append(f'<g class="f-planning-dock"><rect x="{f(x + 12)}" y="{f(dy)}" width="{f(w - 24)}" height="{f(dh)}" rx="8"/>'
             f'<text class="tag f-planning-pt" x="{f(x + 24)}" y="{f(dy + 20)}">EACH STEP</text>')
    fy = dy + 42
    for a, b in fields:
        P.append(f'<text class="sub f-planning-pv" x="{f(x + 24)}" y="{f(fy)}">{escape(a)}</text>')
        if b:
            P.append(f'<text class="sub f-planning-pv" x="{f(x + w - 24)}" y="{f(fy)}" text-anchor="end">{escape(b)}</text>')
        fy += 20
    P.append("</g>")
    P.append(f'<text class="sub f-planning-on" x="{f(x + 16)}" y="{f(dy + dh + 26)}">told the domain</text>')
    h = h or dy + dh + 44 - y
    return (f'<g class="f-planning-pnl"><rect class="panel" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="14" '
            f'style="fill:url(#{pre}-pnl)"/>' + "".join(P) + "</g>", y + h)


def _rules(x, y, w, h, lines, wide):
    P = [f'<g class="card f-planning-rules"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
         f'<text class="tag" x="{f(x + 16)}" y="{f(y + 24)}">{"RULE CHECKS · A STEP IS DROPPED IF" if wide else "RULE CHECKS · DROP A STEP IF"}</text>']
    pitch = 28 if wide else 24
    yy = y + (56 if wide else 50)
    for t in lines:
        P.append(f'<path class="f-planning-rx" d="M{f(x + 18)},{f(yy - 9)} l8,8 M{f(x + 26)},{f(yy - 9)} l-8,8"/>'
                 f'<text class="f-planning-rule" x="{f(x + 36)}" y="{f(yy)}">{escape(t)}</text>')
        yy += pitch
    P.append(f'<text class="lbl" x="{f(x + 16)}" y="{f(yy + 4)}">'
             f'{"core-hours: the model&#39;s own estimate, range-checked only" if wide else "core-hours: range-checked only"}</text>')
    return "".join(P) + "</g>"


def _inputs(x, y, w, wide):
    """CDTP 3.1 and 3.2 cards, the CDTP 3.3 route between them, and the gap list. Returns markup, anchors."""
    P = []
    h1 = 96
    P.append(f'<g class="card f-planning-in"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{h1}" rx="10"/>'
             f'<text class="tag" x="{f(x + 14)}" y="{f(y + 22)}">CDTP 3.1</text>'
             f'<text class="ttl" x="{f(x + 14)}" y="{f(y + 46)}">Request + records</text>'
             f'<text class="sub" x="{f(x + 14)}" y="{f(y + 66)}">no page citations</text>'
             f'<text class="sub" x="{f(x + 14)}" y="{f(y + 86)}">model names 2–5 gaps</text></g>')
    ry = y + h1 + 26
    P.append(f'<g class="f-planning-in"><text class="tag" x="{f(x)}" y="{f(ry)}">CDTP 3.3 ROUTE</text>'
             f'<text class="lbl" x="{f(x)}" y="{f(ry + 18)}">documents given → 3.2</text></g>' if wide else
             f'<g class="f-planning-in"><text class="tag" x="{f(x)}" y="{f(ry)}">CDTP 3.3 ROUTE</text>'
             f'<text class="lbl" x="{f(x + w)}" y="{f(ry)}" text-anchor="end">documents given → 3.2</text></g>')
    y2 = ry + (30 if wide else 14)
    h2 = 130 if wide else 112
    chips = "".join(_chip(x + 14 + k * (56 if wide else 60), y2 + 58, 50 if wide else 54, f"p. {p}") for k, p in enumerate(PAGES))
    ex = (f'<text class="sub" x="{f(x + 14)}" y="{f(y2 + 102)}">≤ 12,000 chars shown</text>'
          f'<text class="sub" x="{f(x + 14)}" y="{f(y2 + 120)}">(tunable default)</text>' if wide else
          f'<text class="sub" x="{f(x + 14)}" y="{f(y2 + 100)}">≤ 12,000 chars shown</text>'
          f'<text class="sub" x="{f(x + w - 14)}" y="{f(y2 + 100)}" text-anchor="end">(default)</text>')
    P.append(f'<g class="card f-planning-in f-planning-act"><rect x="{f(x)}" y="{f(y2)}" width="{f(w)}" height="{h2}" rx="10"/>'
             f'<text class="tag" x="{f(x + 14)}" y="{f(y2 + 22)}">CDTP 3.2</text>'
             f'<text class="tag f-planning-acc" x="{f(x + w - 14)}" y="{f(y2 + 22)}" text-anchor="end">THIS RUN</text>'
             f'<text class="ttl" x="{f(x + 14)}" y="{f(y2 + 46)}">Page-cited excerpts</text>{chips}{ex}</g>')
    y3 = y2 + h2 + (20 if wide else 14)
    h3 = 76
    g = "".join(f'<circle class="f-planning-dot" cx="{f(x + 18)}" cy="{f(y3 + 41.5 + 20 * k)}" r="3"/>'
                f'<text class="sub f-planning-ink" x="{f(x + 28)}" y="{f(y3 + 46 + 20 * k)}">{escape(t)}</text>'
                for k, t in enumerate(GAPS))
    P.append(f'<g class="card f-planning-in"><rect x="{f(x)}" y="{f(y3)}" width="{f(w)}" height="{h3}" rx="10"/>'
             f'<text class="tag" x="{f(x + 14)}" y="{f(y3 + 22)}">GAPS · THE LIST</text>{g}</g>')
    return "".join(P), (y + h1 / 2, y2 + h2 / 2, y3 + h3 / 2, y3 + h3)


def _lane_head(x0, u, top, bottom, axis_y, lbl_x, lbl_y, anchor, grid):
    """Week columns (2,000 core-hours each), the core-hour axis and its label; grid=False leaves the week lines to
    the rows (narrow)."""
    P = []
    for j in range(LANE_MAX // PER_WEEK + 1):
        gx = x0 + j * PER_WEEK * u
        if grid:
            P.append(f'<path class="f-planning-grid" d="M{f(gx)},{f(top)} V{f(bottom)}"/>')
        P.append(f'<path class="f-planning-axis" d="M{f(gx)},{f(axis_y)} v5"/>')
        if j < LANE_MAX // PER_WEEK:  # no 10,000 label: it would run into 8,000
            P.append(f'<text class="sub" x="{f(gx)}" y="{f(axis_y + 20)}" text-anchor="middle">{_n(j * PER_WEEK)}</text>')
    P.append(f'<path class="f-planning-axis" d="M{f(x0)},{f(axis_y)} H{f(x0 + LANE_MAX * u)}"/>')
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    P.append(f'<text class="lbl" x="{f(lbl_x)}" y="{f(lbl_y)}"{a}>cumulative core-hours · 2,000 per week</text>')
    return '<g class="f-planning-lane">' + "".join(P) + "</g>"


def _design(pre, x, y, w, h, wide):
    """The study design: the running core-hour total and the timeline in weeks."""
    return (f'<g class="card f-planning-design"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
            f'<text class="tag" x="{f(x + 14)}" y="{f(y + 22)}">STUDY DESIGN</text>'
            f'<text class="sub f-planning-ink" x="{f(x + w - 14)}" y="{f(y + 22)}" text-anchor="end">{len(VALID)} steps</text>'
            + _odo(pre, x + 14, y + 68)
            + f'<text class="sub" x="{f(x + 132)}" y="{f(y + 52)}">core-hours</text>'
            f'<text class="sub" x="{f(x + 132)}" y="{f(y + 70)}">in total</text>'
            f'<g class="f-planning-wk"><text class="f-planning-wkn" x="{f(x + 14)}" y="{f(y + 102)}">{WEEKS} weeks</text>'
            f'<text class="sub" x="{f(x + 96)}" y="{f(y + 102)}">= ⌈total ÷ 2,000⌉</text></g></g>')


WIDE = {"W": 1100, "H": 1072}


def _wide():
    W, H, pre = WIDE["W"], WIDE["H"], "planning-w"
    P = [_defs(pre), hdr(30, 34, "STUDY DESIGN · CDTP 3.1–3.3")]
    LX, BX, BW, CX = 800, 486, 260, 768
    u = (1070 - LX) / LANE_MAX
    y0, pitch, bh = 108, 100, 88
    P.append(hdr(30, 80, "INPUT") + hdr(246, 80, "DESIGNER") + hdr(BX, 80, "DRAFTED STEPS") + hdr(CX, 80, "CHECK", "middle")
             + hdr(1070, 80, "CORE-HOURS", "end"))
    inp, (a1, a2, a3, gb) = _inputs(30, y0, 192, True)
    P.append(inp)
    pnl, _ = _panel(pre, 246, y0, 210, gb - y0, True)
    # the inputs feed the designer; CDTP 3.1 is the route not taken in this run
    P.append(curve(222, a1, 244, a1 + 20, "cv f-planning-cv f-planning-dash"))
    P.append(_flow(curve_d(222, a2, 244, a2), 0) + _flow(curve_d(222, a3, 244, a3 - 30), .1))
    P.append(pnl)
    last = y0 + 5 * pitch + bh
    P.append(_rules(30, gb + 20, 426, last - gb - 20, RULES, True))
    rules_mid = (gb + 20 + last) / 2
    # the checker: a rail from the rules card down the drafted steps; its nib steps from row to row
    mids = [y0 + i * pitch + bh / 2 for i in range(len(STEPS))]
    P.append(f'<g class="f-planning-rail"><path class="f-planning-rl" d="M470,{y0 + 4} V{last - 4}"/>'
             f'<path class="f-planning-arm" d="M456,{f(rules_mid)} H470"/></g>'
             f'<path class="f-planning-nib" d="M463,{f(mids[0] - 7)} L478,{f(mids[0])} L463,{f(mids[0] + 7)} Z" '
             f'data-ys="{" ".join(f(m - mids[0]) for m in mids)}"/>')
    P.append(_lane_head(LX, u, y0 - 4, last + 6, last + 12, 1070, last + 52, "end", True))
    for i, s in enumerate(STEPS):
        y = y0 + i * pitch
        P.append(_row(i, s, BX, y, BW, bh, (LX, u, y + bh / 2 - 9, 18), (CX, y + bh / 2), True, pre))
    # the decision, the design (yes) or the template (no), then FS
    dy = last + 86
    mid = (last + 40 + dy) / 2
    P.append(_flow(f"M{CX},{last + 4} V{last + 40} C{CX},{f(mid)} {f(BX + BW / 2)},{f(mid)} {f(BX + BW / 2)},{f(dy - 2)}",
                   T["decflow"]))
    P.append(f'<g class="card f-planning-dec"><rect x="{BX}" y="{f(dy)}" width="{BW}" height="58" rx="10"/>'
             f'<text class="tag" x="{BX + 14}" y="{f(dy + 22)}">≥ 2 VALID STEPS?</text>'
             f'<text class="sub f-planning-cnt" x="{BX + 14}" y="{f(dy + 44)}">{len(VALID)} of {len(STEPS)} valid</text>'
             + _ok(BX + BW - 22, dy + 29, "f-planning-ok f-planning-decok") + "</g>")
    ddy = dy + 58 + 30
    P.append(f'<g class="f-planning-yesg"><path class="cv f-planning-yes" d="M{BX + BW / 2},{f(dy + 60)} V{f(ddy - 2)}" marker-end="url(#arr)"/>'
             f'<text class="lbl ok" x="{BX + BW / 2 + 10}" y="{f(dy + 80)}">yes</text></g>')
    P.append(_design(pre, BX, ddy, BW, 124, True))
    sx, sy, sw, sh = 50, dy + 6, 380, 160
    P.append(f'<path class="cv f-planning-no" d="{curve_d(BX - 2, dy + 29, sx + sw + 4, dy + 44)}" marker-end="url(#arr)"/>'
             f'<text class="lbl amb" x="{f(BX - 22)}" y="{f(dy + 22)}" text-anchor="middle">no</text>')
    P.append(_stamp(sx, sy, sw, sh, [("sub", "labelled “template”", None),
                                     ("lbl", "with the reason, when under 2 valid steps", None),
                                     ("lbl", "remain, no language model is available,", None),
                                     ("lbl", "or CDTP 3.2 has no cited evidence", None),
                                     ("lbl amb", "CDTP 3.1 with no records: partial", None)], True))
    gx, gy, gr = 931, dy + 140, 64
    P.append(f'<g class="f-planning-fsg"><path class="cv f-planning-fsc" d="{curve_d(BX + BW + 2, ddy + 36, gx - gr - 16, gy)}" marker-end="url(#arr)"/></g>')
    P.append(hdr(LX + 4, dy + 18, "FS · CDTP 3.3")
             + f'<text class="lbl f-planning-gl" x="{LX + 4}" y="{f(dy + 38)}">scores the finished plan, template too</text>'
             f'<text class="lbl f-planning-gl" x="{LX + 4}" y="{f(dy + 56)}">assesses resources and tools</text>')
    P.append(_gauge(gx, gy, gr))
    P.append(f'<text class="f-planning-fsv" x="{gx}" y="{f(gy + 44)}" text-anchor="middle">{FS}</text>'
             f'<text class="lbl f-planning-gl" x="{gx}" y="{f(gy + 66)}" text-anchor="middle">model-assisted · the run&#39;s own output</text>')
    P.append(legend(LEGEND, 30, H - 38) + note(30, H - 12))
    return svg(W, H, "".join(P), "wide", LABEL)


NARROW = {"W": 360}  # the height follows the layout


def _narrow():
    W, pre = NARROW["W"], "planning-n"
    P = [_defs(pre), hdr(16, 24, "STUDY DESIGN · CDTP 3.1–3.3"),
         '<text class="lbl f-planning-note" x="16" y="44">core-hours: the model&#39;s own estimate</text>']
    P.append(hdr(16, 76, "INPUT"))
    inp, (_, _, _, gb) = _inputs(16, 88, 328, False)
    P.append(inp)
    py = gb + 26
    P.append(_flow(f"M180,{gb + 2} V{py - 2}", 0))
    pnl, pb = _panel(pre, 16, py, 328, None, False)
    P.append(pnl)
    ry = pb + 18
    rh = 50 + 24 * 4 + 16
    P.append(_rules(16, ry, 328, rh, RULES_N, False))
    LX, u = 30, 300 / LANE_MAX
    hy = ry + rh + 30
    P.append(hdr(16, hy, "DRAFTED STEPS") + hdr(344, hy, "CHECK", "end"))
    y0, pitch, bh = hy + 18, 116, 108
    last = y0 + 5 * pitch + bh
    # week columns sit inside each block's lane strip; labels above the first block and the axis below the last
    P.append(_lane_head(LX, u, y0 - 4, last, last + 10, 16, last + 52, "start", False))
    for i, s in enumerate(STEPS):
        y = y0 + i * pitch
        P.append(_row(i, s, 16, y, 328, bh, (LX, u, y + 90, 10), (322, y + 20), False, pre))
    mids = [y0 + i * pitch + bh / 2 for i in range(len(STEPS))]
    P.append(f'<g class="f-planning-rail"><path class="f-planning-rl" d="M8,{y0 + 4} V{last - 4}"/></g>'
             f'<path class="f-planning-nib" d="M2,{f(mids[0] - 6)} L13,{f(mids[0])} L2,{f(mids[0] + 6)} Z" '
             f'data-ys="{" ".join(f(m - mids[0]) for m in mids)}"/>')
    dy = last + 74
    P.append(f'<g class="card f-planning-dec"><rect x="16" y="{f(dy)}" width="328" height="58" rx="10"/>'
             f'<text class="tag" x="30" y="{f(dy + 22)}">≥ 2 VALID STEPS?</text>'
             f'<text class="sub f-planning-cnt" x="30" y="{f(dy + 44)}">{len(VALID)} of {len(STEPS)} valid</text>'
             + _ok(322, dy + 29, "f-planning-ok f-planning-decok") + "</g>")
    ddy = dy + 58 + 28
    P.append(f'<g class="f-planning-yesg"><path class="cv f-planning-yes" d="M180,{f(dy + 60)} V{f(ddy - 2)}" marker-end="url(#arr)"/>'
             f'<text class="lbl ok" x="190" y="{f(dy + 80)}">yes</text></g>')
    P.append(_design(pre, 16, ddy, 328, 116, False))
    gy0 = ddy + 116 + 28
    P.append(f'<g class="f-planning-fsg"><path class="cv f-planning-fsc" d="M180,{f(ddy + 118)} V{f(gy0 - 2)}" marker-end="url(#arr)"/></g>')
    gx, gr = 84, 60
    gy = gy0 + 98
    P.append(hdr(172, gy0 + 16, "FS · CDTP 3.3")
             + "".join(f'<text class="lbl f-planning-gl" x="172" y="{f(gy0 + 38 + 18 * k)}">{t}</text>'
                       for k, t in enumerate(("scores the finished plan,", "template too: assesses", "resources and tools"))))
    P.append(_gauge(gx, gy, gr))
    P.append(f'<text class="f-planning-fsv" x="172" y="{f(gy0 + 110)}">{FS}</text>'
             f'<text class="lbl f-planning-gl" x="172" y="{f(gy0 + 136)}">model-assisted ·</text>'
             f'<text class="lbl f-planning-gl" x="172" y="{f(gy0 + 154)}">the run&#39;s own output</text>')
    sy = gy0 + 172
    sh = 54 + 20 * 5 + 6
    P.append(f'<path class="cv f-planning-no" d="M346,{f(dy + 29)} H353 V{f(sy + 30)} H347" marker-end="url(#arr)"/>'
             f'<text class="lbl amb" x="352" y="{f(dy - 6)}" text-anchor="end">no</text>')
    P.append(_stamp(24, sy, 312, sh, [("sub", "labelled “template”", None),
                                       ("lbl", "with the reason: under 2 valid steps,", None),
                                       ("lbl", "no language model, or 3.2 without", None),
                                       ("lbl", "cited evidence", None),
                                       ("lbl amb", "CDTP 3.1, no records: partial", None)], False))
    H = sy + sh + 24 + 24 * 2 + 30
    P.append("".join(legend(pair, 16, H - 64 + 24 * k) for k, pair in enumerate(LEGEND_N)) + note(16, H - 12))
    return svg(W, H, "".join(P), "narrow", LABEL)


JS = """MAFig.register("planning", function (root, variant) {
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var one = function (s) { return root.querySelector(s); };
  var rows = q(".f-planning-row"), nib = one(".f-planning-nib"), odo = one(".f-planning-odo"),
    needle = one(".f-planning-needle"), fsarc = one(".f-planning-fsarc"), fsv = one(".f-planning-fsv"),
    decok = one(".f-planning-decok"), cnt = one(".f-planning-cnt"), yes = q(".f-planning-yesg"),
    design = one(".f-planning-design"), wk = one(".f-planning-wk"), fsc = q(".f-planning-fsg"),
    bars = q(".f-planning-bar"), strikes = q(".f-planning-strike");
  var A = +needle.getAttribute("data-a"), ys = nib ? nib.getAttribute("data-ys").split(" ").map(Number) : [];
  var odoTop = -(odo.getAttribute("data-n") - 1) * odo.getAttribute("data-pitch"), pitch = +odo.getAttribute("data-pitch");
  gsap.set(bars, {svgOrigin: function (i, el) { return el.getAttribute("data-x0") + " 0"; }});
  gsap.set(needle, {svgOrigin: needle.getAttribute("data-o")});
  // origins set once, at scale 1: an origin passed per tween is smoothed against the from-scale and leaves an offset
  gsap.set(q(".f-planning-num, .f-planning-ok, .f-planning-x, .f-planning-pnl"), {transformOrigin: "50% 50%"});
  var pop = {ease: "back.out(2.2)"};
  // everything a pass reveals by opacity is registered here, and the loop clears exactly this list
  var shown = [], reg = function (x) { shown = shown.concat(x); return x; };
  // one pass from t0. The designer's one call returns the whole list, so all blocks type in first; then the checker
  // nib runs down the rows in order: each check stamps a tick (number, bar) or an amber strike (failing field,
  // reason). After the last check: the decision, the design's total and weeks, and only then the FS needle.
  // Every key in a fromTo start object is repeated in its end object (a loop wrap drops start-only keys).
  function pass(tl, t0) {
    q(".f-planning-flow").forEach(function (el) {
      var t = t0 + +el.getAttribute("data-t");
      tl.fromTo(el, {drawSVG: "0% 0%", opacity: 0}, {drawSVG: "0% 100%", opacity: 1, duration: .5, ease: "power1.in"}, t)
        .to(el, {opacity: 0, duration: .25}, t + .55);
    });
    if (nib) tl.fromTo(nib, {y: 0}, {y: 0, duration: .01}, t0);
    rows.forEach(function (r, i) {
      var ty = t0 + __TY0__ + i * __TS__, tc = t0 + __C0__ + i * __CK__, ok = r.getAttribute("data-ok") === "1",
        wipe = r.querySelector(".f-planning-wipe"), caret = r.querySelector(".f-planning-caret"),
        w = +wipe.getAttribute("data-w"), cw = +caret.getAttribute("data-w");
      tl.fromTo(reg(r.querySelector(".f-planning-blk")), {opacity: 0, x: -8}, {opacity: 1, x: 0, duration: .25}, ty)
        .fromTo(wipe, {attr: {width: 0}}, {attr: {width: w}, duration: .45, ease: "steps(14)"}, ty)
        .fromTo(caret, {x: 0, opacity: 0}, {x: 0, opacity: 1, duration: .01}, ty)
        .to(caret, {x: cw, duration: .45, ease: "steps(14)"}, ty)
        .to(caret, {opacity: 0, duration: .1}, ty + .45);
      if (nib && i) tl.to(nib, {y: ys[i], duration: .2, ease: "power2.inOut"}, tc - .22);
      tl.fromTo(reg(r.querySelector(ok ? ".f-planning-ok" : ".f-planning-x")), {opacity: 0, scale: 1.8},
        Object.assign({opacity: 1, scale: 1, duration: .25}, pop), tc);
      if (ok) {
        tl.fromTo(reg(r.querySelector(".f-planning-num")), {opacity: 0, scale: 0}, Object.assign({opacity: 1, scale: 1, duration: .25}, pop), tc + .12)
          .fromTo(r.querySelector(".f-planning-bar"), {scaleX: 0}, {scaleX: 1, duration: .4, ease: "power3.out"}, tc + .15);
      } else {
        tl.fromTo(r.querySelector(".f-planning-strike"), {drawSVG: "0%"}, {drawSVG: "100%", duration: .2, ease: "none"}, tc + .12)
          .fromTo(reg(gsap.utils.toArray(r.querySelectorAll(".f-planning-badrect, .f-planning-under, .f-planning-why"))), {opacity: 0}, {opacity: 1, duration: .2}, tc + .15);
      }
    });
    tl.fromTo(reg(decok), {opacity: 0, scale: .4}, Object.assign({opacity: 1, scale: 1, duration: .3}, pop), t0 + __DEC__)
      .fromTo(reg(cnt), {opacity: 0}, {opacity: 1, duration: .3}, t0 + __DEC__)
      .fromTo(reg(yes), {opacity: 0}, {opacity: 1, duration: .3}, t0 + __YES__)
      .fromTo(reg(design), {opacity: 0, y: 8}, {opacity: 1, y: 0, duration: .35}, t0 + __DESIGN__)
      .fromTo(odo, {y: odoTop}, {y: odoTop, duration: .01}, t0);
    [__ODO__].forEach(function (t, k) { tl.to(odo, {y: odoTop + (k + 1) * pitch, duration: .22, ease: "power2.out"}, t0 + t); });
    tl.fromTo(reg(wk), {opacity: 0}, {opacity: 1, duration: .3}, t0 + __WEEKS__)
      .fromTo(reg(fsc), {opacity: 0}, {opacity: 1, duration: .3}, t0 + __FSC__)
      .fromTo(fsarc, {drawSVG: "0%"}, {drawSVG: "100%", duration: 1, ease: "power2.out"}, t0 + __NEEDLE__)
      .fromTo(needle, {rotation: -A}, {rotation: 0, duration: __ND__, ease: "elastic.out(1, .45)"}, t0 + __NEEDLE__)
      .fromTo(reg(fsv), {opacity: 0}, {opacity: 1, duration: .3}, t0 + __FSV__);
  }
  var intro = gsap.timeline({defaults: {ease: "power3.out"}});
  intro.from(q(".hdr, .f-planning-note"), {opacity: 0, duration: .5}, 0)
    .from(q(".f-planning-in"), {opacity: 0, x: -10, duration: .35, stagger: .08}, .1)
    .from(q(".f-planning-pnl"), {opacity: 0, scale: .97, duration: .5}, .3)
    .from(q(".f-planning-cv"), {drawSVG: 0, opacity: 0, duration: .4, stagger: .05}, .4)
    .from(q(".f-planning-rules, .f-planning-lane, .f-planning-rail"), {opacity: 0, duration: .4, stagger: .05}, .5)
    .from(q(".f-planning-dec, .f-planning-stamp, .f-planning-no, .f-planning-gbg, .f-planning-gl"), {opacity: 0, duration: .4}, .6)
    .from(q(".legend"), {opacity: 0, duration: .4}, .7);
  pass(intro, __T0I__);
  // loop: hold the finished frame, clear what the pass reveals (registered above), replay. immediateRender off: the
  // frame stays until then.
  var loop = gsap.timeline({repeat: -1, defaults: {immediateRender: false}});
  loop.to(shown, {opacity: 0, duration: .4}, __HOLD__)
    .to(strikes.concat([fsarc]), {drawSVG: "0%", duration: .4}, __HOLD__)
    .to(bars, {scaleX: 0, duration: .4}, __HOLD__)
    .to(needle, {rotation: -A, duration: .4}, __HOLD__);
  if (nib) loop.to(nib, {y: 0, duration: .4, ease: "power2.inOut"}, __HOLD__);
  pass(loop, __T0L__);
  loop.set({}, {}, __TL__);
  return {intro: intro, loop: loop};
});"""
for _k, _v in {"__TY0__": TY0, "__TS__": TS, "__C0__": C0, "__CK__": CK, "__DEC__": T["dec"], "__YES__": T["yes"], "__DESIGN__": T["design"],
               "__ODO__": ", ".join(f"{t:.2f}" for t in T["odo"]), "__WEEKS__": T["weeks"], "__FSC__": T["fsc"],
               "__NEEDLE__": T["needle"], "__ND__": NEEDLE_D, "__FSV__": T["fsv"], "__T0I__": T0_INTRO,
               "__HOLD__": HOLD, "__T0L__": T0_LOOP, "__TL__": T_LOOP}.items():
    JS = JS.replace(_k, _v if isinstance(_v, str) else f"{_v:.2f}".rstrip("0").rstrip("."))
assert "__" not in JS


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
