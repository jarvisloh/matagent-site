"""Modules figure: the five core modules as a zigzag honeycomb ribbon (wide) or a stacked hex column (narrow), each
with a callout card on a leader line saying what the module does (claims C01-C03, C08, C21, C41, C43-C48). Wide is
scrubbed: each hex lights and its callout writes in as the reader scrolls. The SVG is the finished frame."""
import math
from html import escape

from figkit import Figure, f, hdr, icon, legend, svg

# title, icon, callout title, callout lines (<= 22 chars each); order follows the overview slide
MODS = [
    ("SEARCH", "search", "Finds and ranks papers", ["up to five queries", "merged · de-duplicated", "ranked by relevance"]),
    ("PLAN", "plan", "Plans from data gaps", ["queries the database", "lists gaps in the data", "rule-based study plan"]),
    ("AUGMENT", "augment", "Reads and extracts", ["answers cite [p. N]", "reads charts, images", "summarises findings"]),
    ("DISCOVER", "discover", "Builds new tools", ["description → module", "tests run in a sandbox", "chemistry integrations"]),
    ("EVALUATE", "evaluate", "Six model-assisted scores", ["of a run's own output"]),
]
SCORES = [("GCS", "gap closure"), ("FS", "feasibility"), ("RCS", "RAG coverage"),
          ("ICS", "completeness"), ("ARS", "readiness"), ("HFS", "hypotheses")]
LABEL = ("MatAgent's five core modules as a honeycomb, each with a callout. SEARCH turns a question into up to five "
         "queries, merges the results and ranks them by relevance. PLAN queries the database, lists gaps in the data and "
         "makes a rule-based study plan. AUGMENT answers questions citing pages, reads charts and images, and summarises "
         "findings. DISCOVER turns a description into a code module, runs its tests in a sandbox and builds chemistry "
         "integrations. EVALUATE gives six model-assisted scores of a run's own output: GCS gap closure, FS feasibility, "
         "RCS RAG coverage, ICS completeness, ARS readiness and HFS hypotheses.")
LEGEND = [("flow", "core module, no fixed order"), ("dot", "callout: what it does")]

WIDE = {"W": 1100, "H": 690, "R": 86, "gap": 10, "cx": 550, "cy": 366}
# wide callouts: card x, width; every card spans its hex's x so the leader drops straight
WCARDS = [(30, 300), (200, 300), (400, 300), (590, 300), (740, 330)]
NARROW = {"W": 360, "H": 832, "R": 58, "card_x": 148}


def _hexpath(cx, cy, r):
    """Flat-top hexagon (the ribbon tessellates along 30-degree neighbours)."""
    pts = [(cx + r * math.cos(math.radians(60 * k)), cy + r * math.sin(math.radians(60 * k))) for k in range(6)]
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + " Z"


def _cell(i, cx, cy, R, wide):
    name, ic, *_ = MODS[i]
    h = R * math.sqrt(3) / 2
    iy, ty, gy = (cy - h + 22, cy + 8, cy + 34) if wide else (cy - h + 12, cy + 9, cy + 29)
    num = f'<text class="tag" x="{f(cx)}" y="{f(gy)}" text-anchor="middle">0{i + 1}</text>' if wide else ""
    return (f'<g class="f-modules-cell"><path class="hx" d="{_hexpath(cx, cy, R)}"/>'
            f'<path class="f-modules-lit" d="{_hexpath(cx, cy, R - 7)}"/>{icon(ic, cx - 9, iy)}'
            f'<text class="f-modules-hxt" x="{f(cx)}" y="{f(ty)}" text-anchor="middle">'
            f'<tspan class="f-modules-cap">{name[0]}</tspan>{name[1:]}</text>{num}</g>')


def _callout(pre, i, x, y, w, h, wide):
    """Callout card; its text sits in a clip group the intro widens, so the callout writes in."""
    _, _, title, lines, *_ = MODS[i]
    t = [f'<text class="ttl{"" if wide else " sm"}" x="{f(x + 14)}" y="{f(y + 28)}">{escape(title)}</text>']
    if wide:
        t.append(f'<text class="tag" x="{f(x + w - 14)}" y="{f(y + 26)}" text-anchor="end">0{i + 1}</text>')
    for k, s in enumerate(lines):
        t.append(f'<text class="sub" x="{f(x + 14)}" y="{f(y + 52 + 22 * k)}">{escape(s)}</text>')
    if MODS[i][0] == "EVALUATE":
        for k, (ab, what) in enumerate(SCORES):
            if wide:  # two columns of chips
                cw = (w - 36) / 2
                cx_, cy_ = x + 14 + (k % 2) * (cw + 8), y + 66 + (k // 2) * 28
                t.append(f'<rect class="f-modules-chip" x="{f(cx_)}" y="{f(cy_)}" width="{f(cw)}" height="22" rx="6"/>'
                         f'<text class="sub" x="{f(cx_ + 8)}" y="{f(cy_ + 15.5)}"><tspan class="f-modules-sc">{ab}</tspan> {what}</text>')
            else:  # one score per line
                t.append(f'<text class="sub" x="{f(x + 14)}" y="{f(y + 78 + 22 * k)}">'
                         f'<tspan class="f-modules-sc">{ab}</tspan> {what}</text>')
    return (f'<clipPath id="{pre}-c{i}"><rect class="f-modules-wipe" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"/></clipPath>'
            f'<g class="card f-modules-co"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
            f'<g clip-path="url(#{pre}-c{i})">{"".join(t)}</g></g>')


def _lead(x1, y1, x2, y2):
    """Leader line from a callout to its hex, dot on the hex end."""
    return (f'<path class="cv f-modules-lead" d="M{f(x1)},{f(y1)} L{f(x2)},{f(y2)}"/>'
            f'<circle class="f-modules-dot" cx="{f(x2)}" cy="{f(y2)}" r="3.5"/>')


def _wide():
    W, H, R, g, cx, cy = (WIDE[k] for k in ("W", "H", "R", "gap", "cx", "cy"))
    D = math.sqrt(3) * R + g
    dx, dy, h = D * math.cos(math.radians(30)), D / 2, R * math.sqrt(3) / 2
    P = [hdr(30, 34, "FIVE CORE MODULES")]
    # faint cells continue the honeycomb past both ends of the ribbon
    for k in (-1, 5):
        P.append(f'<path class="f-modules-ghost" d="{_hexpath(cx + (k - 2) * dx, cy + dy / 2, R)}"/>')
    top_bottom, low_top = 212, 520  # callouts above the up hexes end at 212; those below the down hexes start at 520
    cells, callouts = [], []
    for i in range(5):
        hx_, hy_ = cx + (i - 2) * dx, cy + (dy / 2 if i % 2 else -dy / 2)
        x, w = WCARDS[i]
        assert x + 20 < hx_ < x + w - 20, MODS[i][0]
        ch = 156 if MODS[i][0] == "EVALUATE" else 112
        if i % 2:
            callouts.append(_lead(hx_, low_top, hx_, hy_ + h) + _callout("modules-w", i, x, low_top, w, ch, True))
        else:
            callouts.append(_lead(hx_, top_bottom, hx_, hy_ - h) + _callout("modules-w", i, x, top_bottom - ch, w, ch, True))
        cells.append(_cell(i, hx_, hy_, R, True))
    P += cells + callouts
    P.append(legend(LEGEND, 30, H - 18))
    return svg(W, H, "".join(P), "wide", LABEL)


def _narrow():
    W, H, R, X = NARROW["W"], NARROW["H"], NARROW["R"], NARROW["card_x"]
    P = [hdr(16, 22, "FIVE CORE MODULES")]
    y, rows = 40, []
    for i in range(5):
        ch = 204 if MODS[i][0] == "EVALUATE" else 112
        rows.append((y, ch, 62 if i % 2 == 0 else 74))  # card top, card height, hex x (a gentle zigzag)
        y += ch + 16
    P.append(f'<path class="f-modules-rail" d="M{rows[0][2]},{rows[0][0] + rows[0][1] / 2} '
             + " ".join(f"L{hx_},{f(t + ch / 2)}" for t, ch, hx_ in rows[1:]) + '"/>')
    for i, (t, ch, hx_) in enumerate(rows):
        hy_ = t + ch / 2
        P.append(_cell(i, hx_, hy_, R, False))
        P.append(_lead(X, hy_, hx_ + R, hy_) + _callout("modules-n", i, X, t, W - 16 - X, ch, False))
    assert y - 16 + 26 <= H - 50  # last card clears the two legend rows
    P.append(legend(LEGEND[:1], 16, H - 36) + legend(LEGEND[1:], 16, H - 12))
    return svg(W, H, "".join(P), "narrow", LABEL)


STEP = 0.9   # seconds between modules in the intro
WIDE_ORDER = [i for i in range(5) if i % 2 == 0] + [i for i in range(5) if i % 2]  # upper row, then lower row

JS = """MAFig.register("modules", function (root, variant) {
  var wide = variant === "wide";
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var cells = q(".f-modules-cell"), cos = q(".f-modules-co"), leads = q(".f-modules-lead"), dots = q(".f-modules-dot"),
    wipes = q(".f-modules-wipe");
  var intro = gsap.timeline({defaults: {ease: "power2.out"}});
  intro.from(q(".hdr"), {opacity: 0, duration: .4}, 0)
    .from(q(".f-modules-ghost, .f-modules-rail"), {opacity: 0, duration: .6}, 0);
  // one module after another: the hex settles, lights, its leader draws and its callout writes in.
  // wide: scrubbed by scroll, so the upper row (callouts above) goes first and the lower row follows as it scrolls into
  // view; narrow: plays once, top to bottom.
  (wide ? %(wide_order)s : [0, 1, 2, 3, 4]).forEach(function (i, n) {
    var c = cells[i], t = .3 + n * %(step)s, up = wide ? i %% 2 === 0 : false;
    intro.from(c, {opacity: 0, scale: .72, transformOrigin: "50%% 50%%", duration: .5}, t)
      .from(c.querySelector(".f-modules-lit"), {opacity: 0, duration: .4}, t + .3)
      .from(dots[i], {scale: 0, transformOrigin: "50%% 50%%", duration: .2}, t + .45)
      .from(leads[i], {drawSVG: "100%% 100%%", duration: .3, ease: "none"}, t + .45)
      .from(cos[i], wide ? {opacity: 0, y: up ? -12 : 12, duration: .3} : {opacity: 0, x: 14, duration: .3}, t + .7)
      .from(wipes[i], {attr: {width: 0}, duration: .55, ease: "power1.inOut"}, t + .8);
  });
  intro.from(q(".legend"), {opacity: 0, duration: .4}, .3 + 4.5 * %(step)s);
  // last, the section's capability-group cards stagger in (static HTML stays visible without JS or with reduced motion)
  var groups = gsap.utils.toArray(root.closest("section").querySelectorAll(".cards .card"));
  intro.from(groups, {opacity: 0, y: 16, duration: .4, stagger: .15}, ">");
  return {intro: intro};
}, {scrub: true});""" % {"step": STEP, "wide_order": WIDE_ORDER}


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
