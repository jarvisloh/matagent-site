"""Modules figure: the five core modules as a zigzag honeycomb ribbon (wide) or a stacked hex column (narrow), flanked
by two dashed context cells, shared memory and a staged agent mode. Each cell has a callout card on a leader line;
each core hex holds a glyph of what its module does (claims C01-C03, C08, C21, C29, C41, C43-C48, C51). Wide is
scrubbed: each hex lights, lit neighbours' seams glow and the callouts write in as the reader scrolls. The SVG is the
finished frame."""
import math
from html import escape

from figkit import Figure, f, flathex, hdr, legend, svg

# cells left to right (wide) / top to bottom (narrow): title, icon, core?, callout title, callout lines (<= 22 chars)
CELLS = [
    ("MEMORY", "memory", False, "Shared memory", ["facts and lessons", "added to each run", "kept for review"]),
    ("SEARCH", "search", True, "Finds and ranks papers", ["up to five queries", "merged · de-duplicated", "ranked by relevance"]),
    ("PLAN", "plan", True, "Plans from data gaps", ["queries the database", "lists gaps in the data", "rule-based study plan"]),
    ("AUGMENT", "augment", True, "Reads and extracts", ["answers cite [p. N]", "reads charts, images", "summarises findings"]),
    ("DISCOVER", "discover", True, "Builds new tools", ["description → module", "tests run in a sandbox", "chemistry integrations"]),
    ("EVALUATE", "evaluate", True, "Six model-assisted scores", ["of a run's own output"]),
    ("NEW MODE", "plug", False, "Staged agent mode", ["from DISCOVER", "handler and test", "awaits promotion"]),
]
SCORES = [("GCS", "gap closure"), ("FS", "feasibility"), ("RCS", "RAG coverage"),
          ("ICS", "completeness"), ("ARS", "readiness"), ("HFS", "hypotheses")]
LABEL = ("MatAgent's five core modules as a honeycomb, each with a callout. SEARCH turns a question into up to five "
         "queries, merges the results and ranks them by relevance. PLAN queries the database, lists gaps in the data and "
         "makes a rule-based study plan. AUGMENT answers questions citing pages, reads charts and images, and summarises "
         "findings. DISCOVER turns a description into a code module, runs its tests in a sandbox and builds chemistry "
         "integrations. EVALUATE gives six model-assisted scores of a run's own output: GCS gap closure, FS feasibility, "
         "RCS RAG coverage, ICS completeness, ARS readiness and HFS hypotheses. Beside them, shared memory adds facts and "
         "lessons to each run and keeps them for review, and DISCOVER stages new agent modes, with a handler and a test, "
         "that await promotion.")
LEGEND = [("hex", "core module, no fixed order"), ("hexdash", "memory · staged mode"), ("dot", "callout: what it does")]
MONO = {"wide": 7.7, "narrow": 8.1}  # Geist Mono advance per character at the text minimum (0.6 em), viewBox units
PAD = 14  # callout text inset; the right padding must be at least 12

WIDE = {"W": 1100, "H": 690, "R": 86, "gap": 10, "cx": 550, "cy": 366}
# wide callouts per cell: card x, width (each card spans its hex's x so the leader drops straight)
WCARDS = [(30, 216), (30, 300), (262, 300), (400, 300), (590, 300), (740, 330), (906, 164)]
NARROW = {"W": 360, "H": 1112, "R": 58, "cx": 64, "card_x": 136}
# reveal start times (s) per cell. Wide (scrubbed): the upper row first; the lower row waits until it has scrolled into
# view, then the group cards. Narrow (plays once): top to bottom, group cards from 2 s.
WIDE_T = [6.8, 0.3, 7.5, 1.5, 8.2, 2.7, 8.9]
WIDE_CARDS_T = 10.3
NARROW_T = [round(.3 + .75 * j, 2) for j in range(7)]
NARROW_CARDS_T = 2.0
REVEAL = 1.35  # a cell's reveal, from settling to its callout fully written


def _glyph(name, wide):
    """Inner glyph, local box x -40..40, y 0..34, of what the module does."""
    if name == "SEARCH":  # ranked results, best first
        return "".join(f'<rect class="f-modules-bar{" on" if k == 0 else ""}" x="-32" y="{2 + 9 * k}" width="{w}" height="5" rx="2.5"/>'
                       for k, w in enumerate((64, 50, 38, 24)))
    if name == "PLAN":  # data coverage grid; the empty cells are the gaps
        gaps = {(2, 0), (5, 1), (1, 2), (4, 2)}
        return "".join(f'<rect class="f-modules-{"ge" if (c, r) in gaps else "gf"}" x="{f(-34.5 + 12 * c)}" y="{12 * r}" width="9" height="9" rx="2"/>'
                       for r in range(3) for c in range(6))
    if name == "AUGMENT":  # a page with the cited passage highlighted, and its citation
        x = -38 if wide else -13
        lines = "".join(f'<path class="f-modules-pl{" on" if y == 20 else ""}" d="M{x + 5},{y} h{16 if y != 26 else 10}"/>' for y in (8, 14, 20, 26))
        cite = '<text class="f-modules-cite" x="-4" y="24">[p. N]</text>' if wide else ""
        return f'<rect class="f-modules-page" x="{x}" y="0" width="26" height="34" rx="3"/>{lines}{cite}'
    if name == "DISCOVER":  # generated code, and a passed check
        code = "".join(f'<path class="f-modules-pl" d="M{-38 + ind},{y} h{w}"/>' for ind, y, w in ((0, 5, 26), (8, 13, 20), (8, 21, 24), (0, 29, 14)))
        return (code + '<circle class="f-modules-okc" cx="24" cy="17" r="11"/>'
                '<use class="f-modules-ok" href="#chk" x="17" y="10" width="14" height="14"/>')
    if name == "EVALUATE":  # a gauge, no scale values
        a = math.radians(180 + .7 * 180)
        ex, ey = 26 * math.cos(a), 30 + 26 * math.sin(a)
        nx, ny = 19 * math.cos(a), 30 + 19 * math.sin(a)
        return (f'<path class="f-modules-arc" d="M-26,30 A26,26 0 0 1 26,30"/>'
                f'<path class="f-modules-arc on" d="M-26,30 A26,26 0 0 1 {f(ex)},{f(ey)}"/>'
                f'<path class="f-modules-needle" d="M0,30 L{f(nx)},{f(ny)}"/><circle class="f-modules-hub" cx="0" cy="30" r="3"/>')
    return ""


def _cell(j, cx, cy, R, wide):
    name, ic, core, *_ = CELLS[j]
    h = R * math.sqrt(3) / 2
    cls = "f-modules-cell" if core else "f-modules-cell f-modules-ctx"
    title = f'<tspan class="f-modules-cap">{name[0]}</tspan>{name[1:]}' if core else name
    if wide:
        isz, iy, ty, gy, gs = 24, cy - 62, cy - 6, cy + 10, 1
    else:
        isz, iy, ty, gy, gs = 18, cy - 42, cy + 2, cy + 10, .62
    if not core:  # context cells: icon and title only, centred
        iy, ty = (cy - 40, cy + 8) if wide else (cy - 30, cy + 9)
    glyph = (f'<g class="f-modules-gl" transform="translate({f(cx)},{f(gy)}) scale({gs})">{_glyph(name, wide)}</g>' if core else "")
    lit = f'<path class="f-modules-lit" d="{flathex(cx, cy, R - 7)}"/>' if core else ""
    return (f'<g class="{cls}"><path class="hx" d="{flathex(cx, cy, R)}"/>{lit}'
            f'<use class="ic" href="#i-{ic}" x="{f(cx - isz / 2)}" y="{f(iy)}" width="{isz}" height="{isz}"/>'
            f'<text class="f-modules-hxt" x="{f(cx)}" y="{f(ty)}" text-anchor="middle">{title}</text>{glyph}</g>')


def _callout(pre, j, x, y, w, h, wide):
    """Callout card; its text sits in a clip group the intro widens, so the callout writes in."""
    name, _, _, title, lines = CELLS[j]
    mono = MONO["wide" if wide else "narrow"]
    for s in lines:
        assert len(s) <= 22 and PAD + len(s) * mono + 12 <= w, (name, s)
    t = [f'<text class="ttl{"" if wide else " sm"}" x="{f(x + PAD)}" y="{f(y + 28)}">{escape(title)}</text>']
    t += [f'<text class="sub" x="{f(x + PAD)}" y="{f(y + 52 + 22 * k)}">{escape(s)}</text>' for k, s in enumerate(lines)]
    if name == "EVALUATE":
        for k, (ab, what) in enumerate(SCORES):
            if wide:  # two columns of chips
                cw = (w - 2 * PAD - 8) / 2
                assert 8 + (len(ab) + 1 + len(what)) * mono + 8 <= cw, (ab, what)
                cx_, cy_ = x + PAD + (k % 2) * (cw + 8), y + 66 + (k // 2) * 28
                t.append(f'<rect class="f-modules-chip" x="{f(cx_)}" y="{f(cy_)}" width="{f(cw)}" height="22" rx="6"/>'
                         f'<text class="sub" x="{f(cx_ + 8)}" y="{f(cy_ + 15.5)}"><tspan class="f-modules-sc">{ab}</tspan> {what}</text>')
            else:  # one score per line
                t.append(f'<text class="sub" x="{f(x + PAD)}" y="{f(y + 78 + 22 * k)}">'
                         f'<tspan class="f-modules-sc">{ab}</tspan> {what}</text>')
    dashed = "" if CELLS[j][2] else " dashed"
    return (f'<clipPath id="{pre}-c{j}"><rect class="f-modules-wipe" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"/></clipPath>'
            f'<g class="card f-modules-co{dashed}"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
            f'<g clip-path="url(#{pre}-c{j})">{"".join(t)}</g></g>')


def _lead(x1, y1, x2, y2):
    """Leader line from a callout to its hex, dot on the hex end."""
    return (f'<path class="cv f-modules-lead" d="M{f(x1)},{f(y1)} L{f(x2)},{f(y2)}"/>'
            f'<circle class="f-modules-dot" cx="{f(x2)}" cy="{f(y2)}" r="3.5"/>')


def _card_h(j):
    return 156 if CELLS[j][0] == "EVALUATE" else 112


def _wide():
    W, H, R, g, cx, cy = (WIDE[k] for k in ("W", "H", "R", "gap", "cx", "cy"))
    D = math.sqrt(3) * R + g
    dx, dy, h = D * math.cos(math.radians(30)), D / 2, R * math.sqrt(3) / 2
    P = [hdr(30, 34, "FIVE CORE MODULES")]
    top_bottom, low_top = 212, 520  # callouts above the up hexes end at 212; those below the down hexes start at 520
    centres = [(cx + (j - 3) * dx, cy + (dy / 2 if j % 2 == 0 else -dy / 2)) for j in range(7)]  # j odd: up row
    cells, callouts, seams = [], [], []
    for j, (hx_, hy_) in enumerate(centres):
        x, w = WCARDS[j]
        assert x + 20 < hx_ < x + w - 20, CELLS[j][0]
        ch = _card_h(j)
        if j % 2:
            callouts.append(_lead(hx_, top_bottom, hx_, hy_ - h) + _callout("modules-w", j, x, top_bottom - ch, w, ch, True))
        else:
            callouts.append(_lead(hx_, low_top, hx_, hy_ + h) + _callout("modules-w", j, x, low_top, w, ch, True))
        cells.append(_cell(j, hx_, hy_, R, True))
    # seams between neighbouring core hexes glow once both are lit
    for a in range(1, 5):
        (x1, y1), (x2, y2) = centres[a], centres[a + 1]
        mx, my, d = (x1 + x2) / 2, (y1 + y2) / 2, math.hypot(x2 - x1, y2 - y1)
        ux, uy = -(y2 - y1) / d * R * .38, (x2 - x1) / d * R * .38
        seams.append(f'<path class="f-modules-seam" data-a="{a}" data-b="{a + 1}" d="M{f(mx - ux)},{f(my - uy)} L{f(mx + ux)},{f(my + uy)}"/>')
    P += cells + seams + callouts
    P.append(legend(LEGEND, 30, H - 18))
    return svg(W, H, "".join(P), "wide", LABEL)


def _narrow():
    W, H, R, hx_, X = NARROW["W"], NARROW["H"], NARROW["R"], NARROW["cx"], NARROW["card_x"]
    assert hx_ + R + 12 <= X
    P = [hdr(16, 22, "FIVE CORE MODULES")]
    y, rows = 40, []
    for j in range(7):
        rows.append((y, 204 if CELLS[j][0] == "EVALUATE" else 112))
        y += rows[-1][1] + 16
    P.append(f'<path class="f-modules-rail" d="M{hx_},{f(rows[0][0] + rows[0][1] / 2)} V{f(rows[-1][0] + rows[-1][1] / 2)}"/>')
    for j, (t, ch) in enumerate(rows):
        hy_ = t + ch / 2
        P.append(_cell(j, hx_, hy_, R, False))
        P.append(_lead(X, hy_, hx_ + R, hy_) + _callout("modules-n", j, X, t, W - 16 - X, ch, False))
    assert y - 16 + 26 <= H - 60 - 14  # last card clears the three legend rows
    P.append("".join(legend([it], 16, H - 60 + 24 * k) for k, it in enumerate(LEGEND)))
    return svg(W, H, "".join(P), "narrow", LABEL)


JS = """MAFig.register("modules", function (root, variant) {
  var wide = variant === "wide", T = wide ? %(wide_t)s : %(narrow_t)s;
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var cells = q(".f-modules-cell"), cos = q(".f-modules-co"), leads = q(".f-modules-lead"), dots = q(".f-modules-dot"),
    wipes = q(".f-modules-wipe");
  var intro = gsap.timeline({defaults: {ease: "power2.out"}});
  intro.from(q(".hdr"), {opacity: 0, duration: .4}, 0);
  if (!wide) intro.from(q(".f-modules-rail"), {opacity: 0, duration: .6}, 0);
  // each cell at its own time (T): the hex settles and lights, its glyph builds, its leader draws and its callout writes
  // in. Wide is scrubbed by scroll: upper row first, the lower row once it has scrolled into view; narrow plays once.
  cells.forEach(function (c, i) {
    var t = T[i], up = wide && i %% 2 === 1, lit = c.querySelector(".f-modules-lit");
    intro.from(c, {opacity: 0, scale: .72, transformOrigin: "50%% 50%%", duration: .5}, t);
    if (lit) intro.from(lit, {opacity: 0, duration: .4}, t + .3)
      .from(c.querySelectorAll(".f-modules-gl > *"), {opacity: 0, duration: .25, stagger: .04}, t + .35);
    var bars = c.querySelectorAll(".f-modules-bar"), needle = c.querySelector(".f-modules-needle");
    if (bars.length) intro.from(bars, {scaleX: 0, transformOrigin: "0%% 50%%", duration: .4, stagger: .06}, t + .35);
    if (needle) intro.from(needle, {rotation: -126, transformOrigin: "0%% 100%%", duration: .6, ease: "back.out(1.6)"}, t + .45);
    intro.from(dots[i], {scale: 0, transformOrigin: "50%% 50%%", duration: .2}, t + .45)
      .from(leads[i], {drawSVG: "100%% 100%%", duration: .3, ease: "none"}, t + .45)
      .from(cos[i], wide ? {opacity: 0, y: up ? -12 : 12, duration: .3} : {opacity: 0, x: 14, duration: .3}, t + .7)
      .from(wipes[i], {attr: {width: 0}, duration: .55, ease: "power1.inOut"}, t + .8);
  });
  // a seam glows, growing from its middle, once both neighbours are lit
  q(".f-modules-seam").forEach(function (s) {
    var t = Math.max(T[+s.getAttribute("data-a")], T[+s.getAttribute("data-b")]) + .4;
    intro.from(s, {drawSVG: "50%% 50%%", opacity: 0, duration: .35}, t);
  });
  intro.from(q(".legend"), {opacity: 0, duration: .4}, wide ? %(wide_cards)s - .4 : 0.3);
  // the section's capability-group cards stagger in (static HTML stays visible without JS or with reduced motion)
  var groups = gsap.utils.toArray(root.closest("section").querySelectorAll(".cards .card"));
  intro.from(groups, {opacity: 0, y: 16, duration: .4, stagger: .15}, wide ? %(wide_cards)s : %(narrow_cards)s);
  return {intro: intro};
}, {scrub: true});""" % {"wide_t": WIDE_T, "narrow_t": NARROW_T, "wide_cards": WIDE_CARDS_T, "narrow_cards": NARROW_CARDS_T}

# wide: the group cards start once every callout has written in
assert max(WIDE_T) + REVEAL <= WIDE_CARDS_T and len(WIDE_T) == len(NARROW_T) == len(CELLS)


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
