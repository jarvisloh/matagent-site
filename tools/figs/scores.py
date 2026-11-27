"""Scores figure: EVALUATE's six scores as an instrument cluster (claims C07, C44, C45, C59, C66, C67).
The dark housing (the one focal panel) holds six 270-degree dials, each labelled with its code, what it measures and a
lamp naming what the score rests on. A run token per score names the modes that produce it and the output EVALUATE reads.
The confirmed scores also carry an inner method ring from the code (C44, C66): GCS one segment per judged gap (closed ones
lit), RCS its three parts (up to 40, 35, 25), HFS its five weighted parts (25, 25, 20, 15, 15); FS, ICS and ARS (C45, C67)
keep a plain dial. In a pass, each run's output appears and its connector draws in, the lamp lights and the ring fills,
and only then does the needle sweep, overshoot slightly and settle, with the readout last. All scores are 0-100; values
are illustrative."""
import math
from html import escape

from figkit import Figure, curve, f, hdr, hexpath, legend, note, svg, vcurve_d

CLAIMS = ("C07", "C44", "C45", "C59", "C66", "C67")  # register rows this figure's text and aria-label rest on

# (code, what it measures, lamp: what the score rests on, run token: modes, run output EVALUATE reads, illustrative value)
SCORES = [("GCS", "Gap closure", "language-model judge", "GAR 2.1", "gaps, papers read", 67),
          ("RCS", "RAG coverage", "term-count formula", "MMR 4.2 · 4.5 · 4.8", "analysis text", 74),
          ("HFS", "Hypothesis formulation", "five weighted parts", "HF 8.4", "hypothesis records", 58),
          ("FS", "Plan feasibility", "resources and tools", "CDTP 3.3", "returned plan", 81),
          ("ICS", "Ingestion completeness", "ingested ÷ expected", "KC 6.2 · 6.4", "ingested items", 88),
          ("ARS", "Tool readiness", "if tests + security", "SE 7.2", "newly created tool", 63)]
for _s in SCORES:
    assert len(_s[2]) <= 20 and len(_s[4]) <= 22 and 0 < _s[5] <= 92, _s
# Inner method ring, confirmed scores only (C44, C66): (segment maxima, illustrative filled share of each, detail line).
# GCS: one segment per judged gap, closed ones full (4 of 6 = 67). RCS: coverage, specificity, calibration parts.
# HFS: the five weights; each part fills weight x its dimension score (60, 70, 50, 40, 63 -> 58).
RING = {"GCS": ([100 / 6] * 6, [1, 1, 1, 1, 0, 0], "4 of 6 gaps closed"),
        "RCS": ([40, 35, 25], [34 / 40, 24 / 35, 16 / 25], "parts: 40, 35, 25 max"),
        "HFS": ([25, 25, 20, 15, 15], [.60, .70, .50, .40, .63], "weights 25/25/20/15/15")}
for _k, (_mx, _fr, _d) in RING.items():
    _s = next(x[5] for x in SCORES if x[0] == _k)
    assert abs(sum(_mx) - 100) < 1e-6 and abs(sum(m * r for m, r in zip(_mx, _fr)) - _s) < .6 and len(_d) <= 22, _k

CW = {"wide": 7.68, "narrow": 8.04}  # Geist Mono advance per character at the sub size
HW = {"wide": 9.73, "narrow": 10.18}  # header advance (0.6 em + .16 em letter-spacing)
TTL_EM = 0.58  # conservative Geist 600 advance per em; ttl.sm is 13.5 px
LBL_EM = 0.52  # Geist italic advance per em (line labels)
SWEEP = 2.7  # degrees per score point: 0 at 225 deg, 100 at -45 deg (a 270-degree dial)

# --- timing (s) within one gauge's beat, then the stagger between gauges ---------------------------------------------
T_FLOW, FLOW_D = .3, .5  # the run's output flows to the gauge after the run token appears
T_LAMP = T_FLOW + FLOW_D  # the method lamp lights when the flow arrives
T_PARTS, PARTS_D, PARTS_ST = T_LAMP + .05, .3, .05  # the method ring's parts fill once the lamp lights
T_NEEDLE, SWEEP_D, SETTLE_D = T_LAMP + .55, .75, .4  # then the needle sweeps past the value and settles back
T_READ = T_NEEDLE + SWEEP_D + SETTLE_D  # the readout starts only once the settle has ended
STAG = .85
PASS = (len(SCORES) - 1) * STAG + T_READ + .3
T0_INTRO, HOLD, T0_LOOP = 1.3, 1.6, 2.2
T_LOOP = T0_LOOP + PASS + .4
assert T0_INTRO + PASS <= 10 and T_LOOP <= 10


def _tv(t):
    return f"{t:.2f}".rstrip("0").rstrip(".")


def _pt(cx, cy, r, s):
    """Point on a dial of centre (cx, cy) at radius r for score s (0-100)."""
    a = math.radians(225 - SWEEP * s)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def _arc(cx, cy, r, s0, s1):
    x0, y0 = _pt(cx, cy, r, s0)
    x1, y1 = _pt(cx, cy, r, s1)
    big = 1 if (s1 - s0) * SWEEP > 180 else 0
    return f"M{f(x0)},{f(y0)} A{r},{r} 0 {big} 1 {f(x1)},{f(y1)}"


def _ring(cx, cy, R, key):
    """The inner method ring (confirmed scores only): one base arc per part, a fill arc for its illustrative share."""
    if key not in RING:
        return ""
    mx, fr, _d = RING[key]
    ri, gap, s0, P = R - 24, .9, 0, ['<g class="f-scores-ring">']
    for m, r in zip(mx, fr):
        a, b = s0 + gap / 2, s0 + m - gap / 2
        P.append(f'<path class="f-scores-seg" d="{_arc(cx, cy, ri, a, b)}"/>')
        if r > 0:
            P.append(f'<path class="f-scores-part" d="{_arc(cx, cy, ri, a, a + (b - a) * r)}"/>')
        s0 += m
    return "".join(P) + "</g>"


def _dial(cx, cy, R, s, key):
    """Face, rim, track, ticks (every 5, major every 25), 0 and 100 under the rim, method ring, value arc, needle, hub,
    readout."""
    rt = R - 14
    P = [f'<g class="f-scores-dial"><circle class="f-scores-rim" cx="{f(cx)}" cy="{f(cy)}" r="{R + 3}"/>'
         f'<circle class="f-scores-face" cx="{f(cx)}" cy="{f(cy)}" r="{R}"/>'
         f'<path class="f-scores-track" d="{_arc(cx, cy, rt, 0, 100)}"/>', _ring(cx, cy, R, key)]
    for k in range(21):
        mj = k % 5 == 0
        x1, y1 = _pt(cx, cy, R - (10 if mj else 8), k * 5)
        x2, y2 = _pt(cx, cy, R - 3, k * 5)
        P.append(f'<path class="f-scores-tk{" mj" if mj else ""}" d="M{f(x1)},{f(y1)} L{f(x2)},{f(y2)}"/>')
    # numerals sit under the rim's lower ends, outside the needle's reach
    ny = cy + R + 11  # clear of the rim's outer edge (R + 4.5)
    P.append(f'<text class="sub f-scores-num" x="{f(cx - .70 * R)}" y="{f(ny)}" text-anchor="middle">0</text>'
             f'<text class="sub f-scores-num" x="{f(cx + .85 * R)}" y="{f(ny)}" text-anchor="middle">100</text></g>')
    # the needle is drawn at the value; the timeline rotates it from 0 (data-a degrees back) about the hub
    a = math.radians(225 - SWEEP * s)
    ux, uy, px, py = math.cos(a), -math.sin(a), math.sin(a), math.cos(a)
    L, T, w = R - 9, 11, 3.2
    pts = [(cx + ux * L, cy + uy * L), (cx + px * w, cy + py * w), (cx - ux * T, cy - uy * T), (cx - px * w, cy - py * w)]
    P.append(f'<path class="f-scores-val" d="{_arc(cx, cy, rt, 0, s)}"/>'
             f'<path class="f-scores-needle" d="M{" L".join(f"{f(x)},{f(y)}" for x, y in pts)} Z" '
             f'data-a="{SWEEP * s:.1f}" data-o="{f(cx)} {f(cy)}"/>'
             f'<circle class="f-scores-hub" cx="{f(cx)}" cy="{f(cy)}" r="6"/>'
             f'<text class="f-scores-read" x="{f(cx)}" y="{f(cy + .62 * R + 2)}" text-anchor="middle">{s}</text>')
    # the readout stays in the dial's bottom gap, which the needle (0-100) and the ring's ends never enter
    assert .62 * R + 2 - 15 > 13 and (R - 24) * math.sqrt(.5) - 2 > 12, R
    return "".join(P)


def _label(tx, cy, code, what, how, room, v):
    """Code, what it measures, the lamp (hollow base; the lit overlay is the part a pass reveals) and, for a ringed
    score, a detail line naming the ring's parts."""
    assert len(what) * 13.5 * TTL_EM <= room and 3 * 26 * .66 <= room, what
    cw = 4 + 12 + len(how) * CW[v] + 7
    assert cw <= room, (how, cw, room)
    return (f'<text class="f-scores-code" x="{f(tx)}" y="{f(cy - 16)}">{code}</text>'
            f'<text class="ttl sm f-scores-pt" x="{f(tx)}" y="{f(cy + 7)}">{escape(what)}</text>'
            f'<circle class="f-scores-lb" cx="{f(tx + 6)}" cy="{f(cy + 26)}" r="4.5"/>'
            f'<g class="f-scores-lamp"><rect x="{f(tx - 4)}" y="{f(cy + 14)}" width="{f(cw)}" height="24" rx="12"/>'
            f'<circle cx="{f(tx + 6)}" cy="{f(cy + 26)}" r="4.5"/></g>'
            f'<text class="sub f-scores-how" x="{f(tx + 16)}" y="{f(cy + 30.5)}">{escape(how)}</text>'
            + (f'<text class="sub f-scores-det" x="{f(tx)}" y="{f(cy + 56)}">{escape(RING[code][2])}</text>' if code in RING else ""))


def _gauge(i, cx, cy, R, tx, room, flow, v):
    code, what, how, _m, _o, s = SCORES[i]
    return (f'<g class="f-scores-gauge" data-k="{code}" data-i="{i}">{_dial(cx, cy, R, s, code)}'
            f'{_label(tx, cy, code, what, how, room, v)}'
            f'<path class="f-scores-flow" d="{flow}" opacity="0"/></g><!--/gauge-->')


def _run(i, hx, hy, r, lx, ly, v, panel):
    """A run token: hexagon with a document icon (the run's output), the modes and what EVALUATE reads."""
    code, _w, _h, modes, out, _s = SCORES[i]
    ic = 18 if r > 18 else 14
    tok = "f-scores-tokp" if panel else "f-scores-tok"
    if panel:  # one line inside the housing: modes, then the output
        texts = (f'<text class="sub f-scores-pi" x="{f(lx)}" y="{f(ly)}">{escape(modes)}</text>'
                 f'<text class="sub f-scores-po" x="{f(lx + len(modes) * CW[v] + 12)}" y="{f(ly)}">{escape(out)}</text>')
    else:
        texts = (f'<text class="ttl sm" x="{f(lx)}" y="{f(ly)}">{escape(modes)}</text>'
                 f'<text class="sub" x="{f(lx)}" y="{f(ly + 20)}">{escape(out)}</text>')
    return (f'<g class="f-scores-run" data-k="{code}"><path class="{tok}" d="{hexpath(hx, hy, r)}"/>'
            f'<use class="ic f-scores-ti" href="#i-augment" x="{f(hx - ic / 2)}" y="{f(hy - ic / 2)}" width="{ic}" height="{ic}"/>'
            f'{texts}</g>')


def _ping(x, y, k):
    return f'<circle class="f-scores-ping" cx="{f(x)}" cy="{f(y)}" r="7" data-i="{k}" opacity="0"/>'


def _defs(pre, arrow=False):
    """Panel gradient; arrow adds the in-panel arrowhead (narrow only: wide connectors use the shared #arr)."""
    m = (f'<marker id="{pre}-arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         '<path d="M0,0 L8,4 L0,8 z" class="f-scores-arrp"/></marker>') if arrow else ""
    return (f'<defs><linearGradient id="{pre}-pnl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="f-scores-g0"/>'
            f'<stop offset="1" class="f-scores-g1"/></linearGradient>{m}</defs>')


LEGEND = [("hex", "a mode's run and its output"), ("flow", "output reaches its gauge"), ("dot", "lamp: what the score rests on")]
LABEL = ("An instrument cluster of EVALUATE's six scores, each a model-assisted measure of a run's own output, not an "
         "independent check; each runs 0–100 but has its own method, so the scores are not comparable. A mode's run "
         "delivers its output, and only then does its gauge's lamp light and its needle settle. "
         "GCS, gap closure, for GAR 2.1: a language model judges whether the papers it read close each gap, 100 × closed ÷ judged, "
         "with word overlap as the fallback. RCS, RAG coverage, for MMR 4.2, 4.5 and 4.8: a term-count formula over the "
         "analysis text, in three parts worth up to 40, 35 and 25. HFS, hypothesis formulation, for HF 8.4: a weighted "
         "sum of five dimensions of each hypothesis record, weights 25, 25, 20, 15 and 15. The inner ring of these three "
         "dials shows those parts; for GCS, one segment per judged gap, closed ones lit. "
         "FS, plan feasibility, for CDTP 3.3: assesses the returned plan against available resources and tools. "
         "ICS, ingestion completeness, for KC 6.2 and 6.4: items ingested ÷ items expected. ARS, tool readiness, for "
         "SE 7.2: a newly created tool's readiness, reported only when test and security results back it. "
         "Values are illustrative.")


def _wide():
    W, R, pre, v = 1100, 54, "sc-w", "wide"
    x0, x1 = 30, 1070
    cwid = (x1 - x0) / 3
    PT, hy_top = 150, 76
    cy1 = PT + 16 + R
    band = cy1 + R + 12  # band top: EVALUATE and the caption line between the rows
    cy2 = band + 36 + 12 + R
    PB = cy2 + R + 22
    hy_bot = PB + 74
    H = hy_bot + 78
    P = [_defs(pre), hdr(30, 30, "SIX SCORES · EACH 0–100")]
    P.append(f'<rect class="panel f-scores-hous" x="{x0}" y="{PT}" width="{x1 - x0}" height="{PB - PT}" rx="18" '
             f'style="fill:url(#{pre}-pnl)"/>')
    by = band + 24
    lbl = "model-assisted measures of a run's own output"
    lx = x0 + 24 + 8 * HW[v] + 18
    P.append(f'<text class="hdr f-scores-pm" x="{x0 + 24}" y="{f(by)}">EVALUATE</text>'
             f'<text class="lbl f-scores-pm" x="{f(lx)}" y="{f(by)}">{lbl}</text>'
             f'<path class="f-scores-rule" d="M{f(lx + len(lbl) * 12.8 * LBL_EM + 16)},{f(by - 4)} H{x1 - 24}"/>')
    runs, gauges, ports = [], [], []
    for i in range(6):
        row, c = divmod(i, 3)
        cx0 = x0 + c * cwid
        cx = cx0 + 20 + R
        cy = cy1 if row == 0 else cy2
        tx = cx + R + 20
        room = cx0 + cwid - 12 - tx
        hx = cx0 + 150
        top = row == 0
        hy = hy_top if top else hy_bot
        ty0, py, ry = (hy + 22, PT, cy - R) if top else (hy - 22, PB, cy + R)
        lx = hx + 32
        assert lx + len(SCORES[i][3]) * 13.5 * TTL_EM <= cx0 + cwid - 4, SCORES[i][3]
        runs.append(_run(i, hx, hy, 22, lx, hy - 3, v, False))
        P.append(curve(hx, ty0, cx, py + (-3 if top else 3), attrs=f'data-i="{i}"', vertical=True))
        ports.append(f'<circle class="f-scores-port" cx="{f(cx)}" cy="{py}" r="4"/>'
                     f'<path class="f-scores-lead" d="M{f(cx)},{py + (4 if top else -4)} V{f(ry + (-3 if top else 3))}"/>'
                     + _ping(cx, py, i))
        flow = vcurve_d(hx, ty0, cx, py) + f" V{f(ry)}"
        gauges.append(_gauge(i, cx, cy, R, tx, room, flow, v))
    P += ports + runs + gauges
    P.append(legend(LEGEND, 30, H - 18) + note(W - 30 - 23 * CW[v], H - 18))
    assert 30 + sum(30 + int(len(t) * 8.1) + 22 for _, t in LEGEND) < W - 30 - 23 * CW[v]
    return svg(W, round(H), "".join(P), v, LABEL)


def _narrow():
    W, R, pre, v = 360, 46, "sc-n", "narrow"
    x0, x1, PT = 12, 348, 40
    P = [_defs(pre, arrow=True), hdr(12, 24, "SIX SCORES · EACH 0–100")]
    rows_y = PT + 104
    pitch = 186
    PB = rows_y + 6 * pitch - 12
    P.append(f'<rect class="panel f-scores-hous" x="{x0}" y="{PT}" width="{x1 - x0}" height="{PB - PT}" rx="18" '
             f'style="fill:url(#{pre}-pnl)"/>')
    lbl1, lbl2 = "model-assisted measures of", "a run's own output"
    assert len(lbl1) * 13.4 * LBL_EM <= x1 - x0 - 32
    P.append(f'<text class="hdr f-scores-pm" x="{x0 + 16}" y="{PT + 30}">EVALUATE</text>'
             f'<text class="lbl f-scores-pm" x="{x0 + 16}" y="{PT + 54}">{lbl1}</text>'
             f'<text class="lbl f-scores-pm" x="{x0 + 16}" y="{PT + 74}">{lbl2}</text>'
             f'<path class="f-scores-rule" d="M{x0 + 16},{PT + 90} H{x1 - 16}"/>')
    runs, gauges = [], []
    for i in range(6):
        y0 = rows_y + i * pitch
        hx, hy = x0 + 22, y0 + 16
        cx, cy = x0 + 14 + R, y0 + 66 + R
        tx = cx + R + 16
        room = x1 - 10 - tx
        lx = hx + 26
        assert lx + (len(SCORES[i][3]) + len(SCORES[i][4])) * CW[v] + 12 <= x1 - 8, SCORES[i]
        runs.append(_run(i, hx, hy, 16, lx, hy + 5, v, True))
        P.append(f'<path class="f-scores-pcv" d="{vcurve_d(hx, hy + 16, cx, cy - R - 6)}" marker-end="url(#{pre}-arr)" data-i="{i}"/>'
                 + _ping(cx, cy - R, i))
        gauges.append(_gauge(i, cx, cy, R, tx, room, vcurve_d(hx, hy + 16, cx, cy - R), v))
    P += runs + gauges
    ly = PB + 34
    P.append("".join(legend([it], 12, ly + 26 * k) for k, it in enumerate(LEGEND)) + note(12, ly + 26 * len(LEGEND)))
    return svg(W, ly + 26 * len(LEGEND) + 14, "".join(P), v, LABEL)


JS = """MAFig.register("scores", function (root, variant) {
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var gauges = q(".f-scores-gauge"), runs = q(".f-scores-run"), pings = q(".f-scores-ping");
  var needles = q(".f-scores-needle"), vals = q(".f-scores-val"), parts = q(".f-scores-part");
  // each run's connector, in gauge order: it draws in behind its run's flow
  var wires = q(".cv[data-i], .f-scores-pcv").sort(function (a, b) { return a.getAttribute("data-i") - b.getAttribute("data-i"); });
  needles.forEach(function (n) { gsap.set(n, {svgOrigin: n.getAttribute("data-o")}); });
  gsap.set(runs, {transformOrigin: "50% 50%"});
  // everything a pass reveals by opacity is registered here, and the loop clears exactly this list
  var shown = [], reg = function (x) { shown = shown.concat(x); return x; };
  // one pass from t0, gauge by gauge: the run's output appears, its flow draws the connector in, the lamp lights and
  // (confirmed scores) the method ring fills; only then does the needle sweep past its value and settle back, with the
  // readout after the settle ends.
  // Every key in a fromTo start object is repeated in its end object (a loop wrap drops start-only keys).
  function pass(tl, t0) {
    gauges.forEach(function (g, i) {
      var t = t0 + i * __STAG__, n = needles[i], A = +n.getAttribute("data-a"), flow = g.querySelector(".f-scores-flow");
      tl.fromTo(reg(runs[i]), {opacity: 0, y: 6}, {opacity: 1, y: 0, duration: .35}, t)
        .fromTo(flow, {drawSVG: "0% 0%", opacity: 1}, {drawSVG: "0% 100%", opacity: 1, duration: __FLOWD__, ease: "power1.in"}, t + __FLOW__)
        .fromTo(reg(wires[i]), {opacity: 0}, {opacity: 1, duration: .25}, t + __LAMP__ - .1)
        .to(flow, {opacity: 0, duration: .3}, t + __LAMP__ + .05)
        .fromTo(pings[i], {opacity: 0, attr: {r: 4}}, {opacity: 1, attr: {r: 4}, duration: .08}, t + __LAMP__ - .1)
        .to(pings[i], {opacity: 0, attr: {r: 13}, duration: .45}, t + __LAMP__ - .02)
        .fromTo(reg(g.querySelector(".f-scores-lamp")), {opacity: 0}, {opacity: 1, duration: .25}, t + __LAMP__);
      var gp = gsap.utils.toArray(g.querySelectorAll(".f-scores-part")), det = g.querySelector(".f-scores-det");
      if (gp.length) tl.fromTo(gp, {drawSVG: "0%"}, {drawSVG: "100%", duration: __PARTSD__, stagger: __PARTSST__, ease: "power2.out"}, t + __PARTS__);
      if (det) tl.fromTo(reg(det), {opacity: 0}, {opacity: 1, duration: .3}, t + __PARTS__);
      tl
        .fromTo(vals[i], {drawSVG: "0%"}, {drawSVG: "100%", duration: __SWEEPD__, ease: "power3.out"}, t + __NEEDLE__)
        .fromTo(n, {rotation: -A}, {rotation: A * .06, duration: __SWEEPD__, ease: "power3.out"}, t + __NEEDLE__)
        .to(n, {rotation: 0, duration: __SETTLED__, ease: "sine.inOut"}, t + __NEEDLE__ + __SWEEPD__)
        .fromTo(reg(g.querySelector(".f-scores-read")), {opacity: 0}, {opacity: 1, duration: .3}, t + __READ__);
    });
  }
  var intro = gsap.timeline({defaults: {ease: "power3.out"}});
  intro.from(q(".hdr:not(.f-scores-pm), .legend"), {opacity: 0, duration: .5}, 0)
    .from(q(".f-scores-hous"), {opacity: 0, scale: .98, transformOrigin: "50% 50%", duration: .5}, .1)
    .from(q(".f-scores-pm, .f-scores-rule, .f-scores-port, .f-scores-lead"), {opacity: 0, duration: .4}, .3)
    .from(q(".f-scores-face, .f-scores-rim"), {opacity: 0, duration: .4, stagger: .06}, .25)
    .from(q(".f-scores-track"), {drawSVG: "0%", duration: .6, stagger: .06}, .35)
    .from(q(".f-scores-tk"), {opacity: 0, duration: .15, stagger: .004}, .4)
    .from(q(".f-scores-seg"), {opacity: 0, duration: .3, stagger: .01}, .5)
    .from(q(".f-scores-num, .f-scores-code, .f-scores-pt, .f-scores-how, .f-scores-lb"), {opacity: 0, duration: .4, stagger: .02}, .6);
  // before the pass: runs and their connectors not yet in, needles at 0, nothing lit or filled, no readouts
  intro.set(runs.concat(wires, q(".f-scores-lamp, .f-scores-read, .f-scores-det")), {opacity: 0}, 0)
    .set(vals.concat(parts), {drawSVG: "0%"}, 0)
    .set(needles, {rotation: function (i, n) { return -n.getAttribute("data-a"); }}, 0)
    .set(q(".f-scores-flow"), {drawSVG: "0% 0%"}, 0);
  pass(intro, __T0I__);
  // loop: hold the finished frame, clear what the pass reveals (registered above), drop the needles, replay.
  // immediateRender off: the frame stays until then.
  var loop = gsap.timeline({repeat: -1, defaults: {immediateRender: false}});
  loop.to(shown, {opacity: 0, duration: .4}, __HOLD__)
    .to(vals.concat(parts), {drawSVG: "0%", duration: .4}, __HOLD__)
    .to(needles, {rotation: function (i, n) { return -n.getAttribute("data-a"); }, duration: .45, ease: "power2.in"}, __HOLD__);
  pass(loop, __T0L__);
  loop.set({}, {}, __TL__);
  return {intro: intro, loop: loop};
});"""
for _k, _v in {"__STAG__": STAG, "__FLOWD__": FLOW_D, "__FLOW__": T_FLOW, "__LAMP__": T_LAMP, "__SWEEPD__": SWEEP_D, "__PARTS__": T_PARTS, "__PARTSD__": PARTS_D, "__PARTSST__": PARTS_ST,
               "__NEEDLE__": T_NEEDLE, "__SETTLED__": SETTLE_D, "__READ__": T_READ, "__T0I__": T0_INTRO, "__HOLD__": HOLD,
               "__T0L__": T0_LOOP, "__TL__": T_LOOP}.items():
    JS = JS.replace(_k, _tv(_v))
assert "__" not in JS


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
