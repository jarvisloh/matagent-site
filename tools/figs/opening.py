"""Opening figure: the MatAgent core in a honeycomb of the five core modules and shared memory, inside a dial with a
radar sweep. A question enters through chat, agent modes or MCP; artefacts come back (claims C41-C45, C01-C03, C20,
C21, C24, C27-C29, C35, C36, C39; C72, assumed, for the sandbox checks). The SVG is the finished frame; the GSAP intro animates from hidden states."""
import math
from html import escape

from figkit import Figure, curve, f, hdr, hexpath, icon, legend, svg

CLAIMS = ("C01", "C02", "C03", "C20", "C21", "C24", "C27", "C28", "C29", "C35", "C36", "C39", "C41", "C42", "C43", "C44", "C45", "C72")  # register rows this figure's text and aria-label rest on

T = 9.0       # one sweep, s
T_LOOP = 10.4  # sweep, then the run record is saved before the next sweep
R0 = 232      # sweep angle in the static frame and at loop start (deg, SVG: clockwise from +x)
WIDE = {"W": 1100, "H": 616, "cx": 550, "cy": 300}
NARROW = {"W": 360, "H": 1196, "cx": 180, "cy": 488}

# angle around the core, title, sub-label, icon
CELLS = [
    (240, "SEARCH", "find · rank", "search"),
    (300, "AUGMENT", "read · extract", "augment"),
    (0, "PLAN", "gaps · plans", "plan"),
    (60, "DISCOVER", "code · tools", "discover"),
    (120, "EVALUATE", "six scores", "evaluate"),
    (180, "MEMORY", "facts · lessons", "memory"),
]
CELL_T = [round(((a - R0) % 360) / 360 * T, 3) for a, *_ in CELLS]  # when the sweep's leading edge passes each cell
# artefact title, sub-label, source tag, tick time: the five module artefacts tick as their cell lights;
# the run record comes from the run registry (C28), so it ticks once the sweep has finished
ARTS = [
    ("Ranked papers", "merged · de-duplicated", "SEARCH", CELL_T[0]),
    ("Cited answers", "pages cited as [p. N]", "AUGMENT", CELL_T[1]),
    ("Study plan", "model or rule-based", "PLAN", CELL_T[2]),
    ("New modules", "code + sandbox checks", "DISCOVER", CELL_T[3]),
    ("Run scores", "model-assisted", "EVALUATE", CELL_T[4]),
    ("Run record", "input, outputs, events", "EACH RUN", T),
]
ASKS = [("chat", "Chat", "tool use · operations"), ("chain", "Agent modes", "single runs · chains"),
        ("plug", "MCP server", "ten tools · stdio, SSE")]
QUESTION = ("Which dopants stabilise", "Ni-rich layered oxides?")
LABEL = ("MatAgent schematic: a question reaches MatAgent through chat, agent modes or the MCP server. The chat agent "
         "starts modes, which run on five core modules, SEARCH, PLAN, AUGMENT, DISCOVER and EVALUATE, with shared "
         "memory. A run returns ranked papers, answers that cite pages, a study plan, new code modules checked in a "
         "sandbox and model-assisted run scores, and each run is saved as a record.")
LEGEND = [("flow", "schematic sweep, no fixed order"), ("dot", "artefact returned")]
RECORD_GAP = 12  # extra space sets the run record apart from the module artefacts


def _pt(cx, cy, d, a):
    return cx + d * math.cos(math.radians(a)), cy + d * math.sin(math.radians(a))


def _memkey(x, y):
    return (f'<g class="legend" transform="translate({f(x)},{f(y)})"><path d="M0,-4 h22" class="f-opening-memkey"/>'
            '<text x="30" y="0">shared memory</text></g>')


def _flower(pre, cx, cy, R, gap, core_r, ring, tick):
    """Dial, sweep wedge, six cells and the dark core. Returns markup; cells carry data-dx/dy (offset from the core)."""
    D = math.sqrt(3) * (R + gap)
    P = [f'<defs><radialGradient id="{pre}-core" cx="50%" cy="42%" r="62%"><stop offset="0" class="f-opening-g0"/>'
         f'<stop offset="1" class="f-opening-g1"/></radialGradient>'
         f'<linearGradient id="{pre}-sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" class="f-opening-s0" stop-opacity="0"/>'
         f'<stop offset="1" class="f-opening-s1" stop-opacity=".22"/></linearGradient>'
         f'<clipPath id="{pre}-clip"><circle cx="{cx}" cy="{cy}" r="{ring}"/></clipPath></defs>']
    ticks = "".join(
        f'<line x1="{f(_pt(cx, cy, ring + 2, a)[0])}" y1="{f(_pt(cx, cy, ring + 2, a)[1])}" '
        f'x2="{f(_pt(cx, cy, ring + (tick if a % 30 == 0 else tick * .6), a)[0])}" '
        f'y2="{f(_pt(cx, cy, ring + (tick if a % 30 == 0 else tick * .6), a)[1])}"/>' for a in range(0, 360, 6))
    P.append(f'<circle class="f-opening-ring" cx="{cx}" cy="{cy}" r="{ring}"/><g class="f-opening-ticks">{ticks}</g>')
    (lx, ly), (tx, ty) = _pt(cx, cy, ring, R0), _pt(cx, cy, ring, R0 - 40)
    P.append(f'<g clip-path="url(#{pre}-clip)"><path class="f-opening-sweep" fill="url(#{pre}-sweep)" '
             f'd="M{cx},{cy} L{f(lx)},{f(ly)} A{ring},{ring} 0 0 0 {f(tx)},{f(ty)} Z"/></g>')
    wide = pre.endswith("-w")
    for ang, ttl, sub, ic in CELLS:
        hx, hy = _pt(cx, cy, D, ang)
        mem = " f-opening-mem" if ttl == "MEMORY" else ""
        title = ttl if mem else f'<tspan class="f-opening-cap">{ttl[0]}</tspan>{ttl[1:]}'
        if wide:
            iy, ty_, lines = hy - 48, hy + 4, [(sub, hy + 26)]
        else:  # narrow hexes are too slim for a 14-character sub-label at 13.4 units, so every one stacks
            parts = sub.split(" · ") if " · " in sub else sub.split(" ", 1)
            iy, ty_, lines = hy - 46, hy - 6, list(zip(parts, (hy + 15, hy + 34)))
        subs = "".join(f'<text class="sub" x="{f(hx)}" y="{f(y)}" text-anchor="middle">{escape(t)}</text>' for t, y in lines)
        P.append(f'<g class="f-opening-cell{mem}" data-dx="{f(hx - cx)}" data-dy="{f(hy - cy)}">'
                 f'<path class="hx" d="{hexpath(hx, hy, R)}"/>{icon(ic, hx - 9, iy)}'
                 f'<text class="f-opening-hxt" x="{f(hx)}" y="{f(ty_)}" text-anchor="middle">{title}</text>{subs}'
                 f'<path class="f-opening-trace" d="{hexpath(hx, hy, R)}" opacity="0"/></g>')
    # "chat agent · modes" stacks: at the shared minimum size it is wider than the core hex
    subs = "".join(f'<text class="sub f-opening-on" x="{cx}" y="{cy + dy}" text-anchor="middle">{s}</text>'
                   for s, dy in (("chat agent", 14), ("modes", 33)))
    P.append(f'<g class="f-opening-core"><path class="hx f-opening-corehex" style="fill:url(#{pre}-core)" '
             f'd="{hexpath(cx, cy, core_r)}"/><circle class="f-opening-pulse" cx="{cx}" cy="{cy - 42}" r="3"/>'
             f'<text class="f-opening-core1" x="{cx}" y="{cy - 8}" text-anchor="middle">MatAgent</text>'
             f'{subs}</g>')
    return "".join(P)


def _art(x, y, w, h, i, variant):
    title, sub, tag, _ = ARTS[i]
    tx, ty, sy, gy, dy = (x + 16, y + 24, y + 45, y + 21, y + 41) if variant == "wide" else (x + 14, y + 22, y + 43, y + 20, y + 38)
    return (f'<g class="card f-opening-art"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
            f'<text class="ttl" x="{f(tx)}" y="{f(ty)}">{escape(title)}</text>'
            f'<text class="sub" x="{f(tx)}" y="{f(sy)}">{escape(sub)}</text>'
            f'<text class="tag" x="{f(x + w - 14)}" y="{f(gy)}" text-anchor="end">{escape(tag)}</text>'
            f'<circle class="f-opening-ripple" cx="{f(x + w - 20)}" cy="{f(dy)}" r="5" opacity="0"/>'
            f'<circle class="f-opening-ok" cx="{f(x + w - 20)}" cy="{f(dy)}" r="5"/></g>')


def _wide():
    W, H, cx, cy = WIDE["W"], WIDE["H"], WIDE["cx"], WIDE["cy"]
    ax = W - 260  # artefact column
    P = [hdr(30, 44, "A QUESTION"), hdr(ax, 44, "WHAT COMES BACK")]
    P.append(_flower("opening-w", cx, cy, 76, 6, 78, 232, 14))
    # left: the question and the three ways in
    P.append(f'<g class="card f-opening-ask"><rect x="30" y="76" width="230" height="118" rx="12"/>{icon("chat", 46, 91)}'
             '<text class="tag" x="72" y="104">ILLUSTRATIVE</text>'
             f'<text class="f-opening-qt" x="46" y="138">{QUESTION[0]}</text><text class="f-opening-qt" x="46" y="160">{QUESTION[1]}</text>'
             '<text class="sub" x="46" y="184">domain · ceramic</text></g>')
    for j, (ic, t, s) in enumerate(ASKS):
        y = 214 + j * 64
        P.append(f'<g class="card f-opening-ask"><rect x="30" y="{y}" width="230" height="54" rx="10"/>{icon(ic, 46, y + 18)}'
                 f'<text class="ttl" x="74" y="{y + 23}">{t}</text><text class="sub" x="74" y="{y + 42}">{escape(s)}</text></g>')
        P.append(curve(260, y + 27, cx - 248, cy, cls="cv f-opening-in", arrow=j == 1))
    P.append(curve(260, 241, cx - 248, cy, cls="f-opening-flow f-opening-inflow", arrow=False, attrs='opacity="0"'))
    P.append('<text class="lbl" x="264" y="226">asks</text>')
    # right: one artefact per module, plus the run record, fanned out of the dial
    for i in range(len(ARTS)):
        y = 76 + i * 78 + (RECORD_GAP if i == 5 else 0)
        P.append(curve(cx + 250, cy, ax - 2, y + 29, cls="cv f-opening-out"))
        P.append(curve(cx + 250, cy, ax - 2, y + 29, cls="f-opening-flow f-opening-outflow", arrow=False, attrs='opacity="0"'))
        P.append(_art(ax, y, 230, 58, i, "wide"))
    P.append(legend(LEGEND, 30, H - 20) + _memkey(30 + 492, H - 20))
    return svg(W, H, "".join(P), "wide", LABEL)


def _narrow():
    W, H, cx, cy = NARROW["W"], NARROW["H"], NARROW["cx"], NARROW["cy"]
    P = [hdr(16, 22, "A QUESTION")]
    P.append(f'<g class="card f-opening-ask"><rect x="16" y="34" width="328" height="92" rx="12"/>{icon("chat", 30, 49)}'
             '<text class="tag" x="56" y="62">ILLUSTRATIVE</text><text class="sub" x="330" y="62" text-anchor="end">domain · ceramic</text>'
             f'<text class="f-opening-qt" x="30" y="92">{QUESTION[0]}</text><text class="f-opening-qt" x="30" y="114">{QUESTION[1]}</text></g>')
    for j, (ic, t, s) in enumerate(ASKS):
        y = 138 + j * 48
        P.append(f'<g class="card f-opening-ask"><rect x="16" y="{y}" width="328" height="40" rx="10"/>{icon(ic, 28, y + 11)}'
                 f'<text class="ttl sm" x="54" y="{y + 25}">{t}</text>'
                 f'<text class="sub" x="330" y="{y + 25}" text-anchor="end">{escape(s)}</text></g>')
    P.append(f'<path class="cv f-opening-in" d="M{cx},278 V{cy - 180}" marker-end="url(#arr)"/>'
             f'<path class="f-opening-flow f-opening-inflow" d="M{cx},278 V{cy - 180}" opacity="0"/>'
             f'<text class="lbl" x="{cx + 10}" y="298">asks</text>')
    # R 57 + gap 6: hex corners sit 9 units inside the ring, cells 10 apart
    P.append(_flower("opening-n", cx, cy, 57, 6, 59, 170, 6))
    top = cy + 180
    P.append(hdr(40, top + 48, "WHAT COMES BACK"))
    ys = [top + 60 + i * 62 + (RECORD_GAP if i == 5 else 0) for i in range(len(ARTS))]
    spine = f"M{cx},{top} C{cx},{top + 16} 24,{top} 24,{top + 22}"  # clears the header before it drops to the cards
    P.append(f'<path class="cv f-opening-out" d="{spine} V{ys[-1] + 27}"/>')
    for i, y in enumerate(ys):
        P.append(f'<path class="cv f-opening-out" d="M24,{y + 27} H38" marker-end="url(#arr)"/>'
                 f'<path class="f-opening-flow f-opening-outflow" d="{spine} V{y + 27} H38" opacity="0"/>')
        P.append(_art(40, y, 304, 54, i, "narrow"))
    P.append(legend(LEGEND[:1], 16, H - 60) + legend(LEGEND[1:], 16, H - 36) + _memkey(16, H - 12))
    return svg(W, H, "".join(P), "narrow", LABEL)


JS = """MAFig.register("opening", function (root, variant) {
  var wide = variant === "wide", G = wide ? %(wide)s : %(narrow)s;
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var org = G.cx + " " + G.cy, cells = q(".f-opening-cell"), arts = q(".f-opening-art");
  var slide = function (d) { return wide ? {x: d} : {y: Math.abs(d) / 2}; };
  var intro = gsap.timeline({defaults: {ease: "power3.out"}});
  intro.from(q(".hdr"), {opacity: 0, duration: .5}, 0)
    .from(q(".f-opening-core"), {opacity: 0, scale: .7, transformOrigin: "50%% 50%%", duration: .6}, 0)
    // hexes assemble outward from the core, in sweep order; offsets keep every hex clear of its neighbours
    .from(cells, {opacity: 0, scale: .6, transformOrigin: "50%% 50%%", duration: .7, stagger: .1,
      x: function (i, el) { return -.15 * el.getAttribute("data-dx"); },
      y: function (i, el) { return -.15 * el.getAttribute("data-dy"); }}, .35)
    .from(q(".f-opening-ring"), {drawSVG: 0, duration: 1.2, ease: "power2.inOut"}, .7)
    .from(q(".f-opening-ticks line"), {opacity: 0, duration: .3, stagger: .015}, .7)
    .from(q(".f-opening-ask"), Object.assign({opacity: 0, duration: .5, stagger: .1}, slide(-24)), .3)
    .from(q(".f-opening-in"), {drawSVG: 0, opacity: 0, duration: .5}, 1.0)
    .from(q(".lbl"), {opacity: 0, duration: .4}, 1.2)
    .from(q(".f-opening-out"), {drawSVG: 0, opacity: 0, duration: .6, stagger: .06}, 1.4)
    .from(arts, Object.assign({opacity: 0, duration: .5, stagger: .08}, slide(24)), 1.5)
    .from(q(".f-opening-ok"), {scale: 0, transformOrigin: "50%% 50%%", duration: .4, stagger: .08, ease: "back.out(3)"}, 1.9)
    .from(q(".f-opening-sweep"), {opacity: 0, duration: .6}, 1.9)
    .from(q(".legend"), {opacity: 0, duration: .5}, 2.1);
  // every property a loop tween sets appears in its to-vars too: from-only values live in startAt, which a rewind
  // (each loop wrap) reverts and the next pass does not re-apply, so traces and pulses would vanish after one loop.
  // loop: the sweep turns once; as it passes a cell, the cell's outline traces; each artefact gets a pulse and a tick
  // at its own time (the run record after the sweep). immediateRender off: the finished frame stays until reached.
  var T = %(T)s, TL = %(TL)s, CELL_T = %(cell_t)s, ART_T = %(art_t)s;
  var loop = gsap.timeline({repeat: -1, defaults: {immediateRender: false}});
  var sweep = q(".f-opening-sweep"), ticks = q(".f-opening-ticks"), flows = q(".f-opening-outflow");
  gsap.set(sweep.concat(ticks), {svgOrigin: org});
  loop.fromTo(sweep, {rotation: 0}, {rotation: 360, duration: T, ease: "none"}, 0)
    .fromTo(ticks, {rotation: 0}, {rotation: 30, duration: TL, ease: "none"}, 0)
    .fromTo(q(".f-opening-pulse"), {opacity: 1}, {opacity: .25, duration: TL / 8, yoyo: true, repeat: 7, ease: "sine.inOut"}, 0)
    .fromTo(q(".f-opening-inflow"), {drawSVG: "0%% 0%%", opacity: 1}, {drawSVG: "85%% 100%%", opacity: 1, duration: .5, ease: "power1.in"}, 0)
    .to(q(".f-opening-inflow"), {opacity: 0, duration: .15}, .5);
  CELL_T.forEach(function (t, i) {
    var tr = cells[i].querySelector(".f-opening-trace");
    loop.fromTo(tr, {drawSVG: "0%%", opacity: 1}, {drawSVG: "100%%", opacity: 1, duration: .6, ease: "power1.inOut"}, t)
      .to(tr, {opacity: 0, duration: .35}, t + .8);
  });
  ART_T.forEach(function (t, i) {
    var ok = arts[i].querySelector(".f-opening-ok"), rp = arts[i].querySelector(".f-opening-ripple");
    loop.fromTo(flows[i], {drawSVG: "0%% 12%%", opacity: 1}, {drawSVG: "88%% 100%%", opacity: 1, duration: .5, ease: "power1.in"}, t + .2)
      .to(flows[i], {opacity: 0, duration: .12}, t + .7)
      .fromTo(rp, {attr: {r: 5}, opacity: .9}, {attr: {r: 15}, opacity: 0, duration: .55, ease: "power2.out"}, t + .75)
      .fromTo(ok, {scale: 1}, {scale: 1.5, transformOrigin: "50%% 50%%", duration: .15, yoyo: true, repeat: 1}, t + .72);
  });
  return {intro: intro, loop: loop};
});""" % {"wide": '{cx: %d, cy: %d}' % (WIDE["cx"], WIDE["cy"]), "narrow": '{cx: %d, cy: %d}' % (NARROW["cx"], NARROW["cy"]),
          "T": T, "TL": T_LOOP, "cell_t": CELL_T, "art_t": [a[3] for a in ARTS]}

# every loop event (record ripple ends at its tick + 1.3 s) finishes inside the loop period
assert max(t for *_, t in ARTS) + 1.3 <= T_LOOP and max(CELL_T) + 1.15 <= T_LOOP


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
