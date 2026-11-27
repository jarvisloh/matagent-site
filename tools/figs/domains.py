"""Domains figure: ten material domains as a honeycomb of flip tiles around the domain profile (claims C13, C14, C24).
Front of a tile: index, icon, domain. Back: the checks its profile names, hard (amber dot: a fail rejects) or soft
(ring: a fail lowers the rank). A ripple leaves the profile (the one dark panel) and runs through the seams of the
lattice; each tile turns over when the wave front reaches it, and only then do its pips light in the check key. A
second ripple turns the tiles back. The SVG is the finished frame (fronts up, every pip lit). Hover or keyboard focus
turns a tile through CSS alone, so it works without GSAP; the timeline only sets each tile's data-flip attribute."""
import math
from html import escape

from figkit import ICONS, Figure, f, hdr, legend, svg

NB = " "  # narrow no-break space before %
SQ3 = math.sqrt(3)

# C24 (profile "checks"), MatPlat order. Index = position in this list.
DOMAINS = [("Catalyst", "catalyst", ("comp", "charge")), ("Semiconductor", "semiconductor", ("charge", "radius")),
           ("Polymer", "polymer", ("smiles",)), ("Metal", "metal", ("comp",)), ("Ceramic", "ceramic", ("charge", "radius")),
           ("MOF", "mof", ("smiles",)), ("Zeolite", "zeolite", ("iza", "sial")), ("Nanomaterial", "nano", ("charge",)),
           ("Composite", "composite", ("comp",)), ("Biomaterial", "bio", ("smiles", "charge"))]
# key: (hard, tile text, key title, key sub, aria text). Hard checks reject on a fail (C13); soft ones lower the rank (C14).
CHECKS = {
    "smiles": (True, "SMILES sanitises", "SMILES sanitises", "RDKit · reads SMILES", "SMILES sanitises (RDKit)"),
    "iza": (True, "IZA framework code", "IZA framework code", "reads framework code", "IZA framework code"),
    "sial": (True, "Si/Al ≥ 1", "Si/Al ≥ 1", "Löwenstein's rule", "Si/Al ≥ 1 (Löwenstein's rule)"),
    "comp": (True, "composition sum", f"Composition sum ≤ 101{NB}%", "at%, wt%, mol%, vol%", f"composition sum ≤ 101{NB}%"),
    "charge": (False, "charge balance", "Charge balance", "oxidation-state guess", "charge balance"),
    "radius": (False, "radius mismatch", f"Radius mismatch ≤ 30{NB}%", "Shannon radii, CN 6", f"dopant–host radius mismatch ≤ 30{NB}%"),
}
for _n, _ic, _cs in DOMAINS:
    assert f"dm-{_ic}" in ICONS and 1 <= len(_cs) <= 2 and all(c in CHECKS for c in _cs), _n

HARD_TXT, SOFT_TXT = "a fail rejects the hypothesis", "a fail lowers its rank"
CW = {"wide": 7.68, "narrow": 8.04}  # Geist Mono advance per character at the sub size
HW = {"wide": 9.73, "narrow": 10.18}  # header advance (0.6 em + .16 em letter-spacing)
TAGW = {"wide": 9.22, "narrow": 9.65}  # tag advance (0.6 em + .12 em letter-spacing)
TTLW = 7.9  # conservative Geist 600 13.5 px advance (ttl.sm)

# --- timing (s). A pass: ripple out (tiles turn to their checks, pips light), hold, ripple back (fronts again) ---------
WAVE_S = .8  # seconds per lattice pitch
PIP_LAG = .42  # a pip lights after its tile's back has turned fully (CSS flip: 2 x .18 s)
HOLD_BACKS = 2.2  # backs stay up at least this long after the last tile turns
T0_INTRO, HOLD, T0_LOOP = 1.3, 1.6, 2.2


def _hex(cx, cy, r):
    """Pointy-top hexagon path."""
    pts = [(cx + r * math.cos(math.radians(-90 + 60 * k)), cy + r * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + " Z"


def _halfw(R, dy):
    """Half-width of a pointy-top hexagon of circumradius R at vertical offset dy from its centre."""
    return SQ3 * R / 2 if abs(dy) <= R / 2 else SQ3 * (R - abs(dy))


def _fits(R, dy_top, dy_bot, w, pad=5):
    assert w / 2 + pad <= min(_halfw(R, dy_top), _halfw(R, dy_bot)), (R, dy_top, dy_bot, w)


def _tv(t):
    return f"{t:.2f}".rstrip("0").rstrip(".")


def _glyph(x, y, hard, r=4.5):
    return f'<circle class="f-domains-{"hard" if hard else "soft"}" cx="{f(x)}" cy="{f(y)}" r="{r}"/>'


def _tile_label(name, checks):
    hard = [CHECKS[c][4] for c in checks if CHECKS[c][0]]
    soft = [CHECKS[c][4] for c in checks if not CHECKS[c][0]]
    parts = []
    if hard:
        parts.append(f"hard check{'s' if len(hard) > 1 else ''}, {HARD_TXT}: " + "; ".join(hard))
    if soft:
        parts.append(f"soft check{'s' if len(soft) > 1 else ''}, {SOFT_TXT}: " + "; ".join(soft))
    return f"{name}. " + ". ".join(p[0].upper() + p[1:] for p in parts) + "."


def _tile(i, cx, cy, R, dt, v):
    name, ic, checks = DOMAINS[i]
    idx = f"{i + 1:02d}"
    cw, hw = CW[v], HW[v]
    hx = _hex(cx, cy, R)
    # front: index, icon, name
    _fits(R, -59, -47, 2 * cw)
    _fits(R, -34, 22, len(name) * 8.4)
    front = (f'<g class="f-domains-face f-domains-front"><path class="f-domains-fx" d="{hx}"/>'
             f'<text class="sub f-domains-ix" x="{f(cx)}" y="{f(cy - 50)}" text-anchor="middle">{idx}</text>'
             f'<use class="ic f-domains-ic" href="#i-dm-{ic}" x="{f(cx - 16)}" y="{f(cy - 40)}" width="32" height="32"/>'
             f'<text class="ttl" x="{f(cx)}" y="{f(cy + 18)}" text-anchor="middle">{escape(name)}</text></g>')
    # back: index, name, then its checks (glyph + text) as a left-aligned block centred in the hex
    _fits(R, -32, -18, len(name) * hw)
    texts = [CHECKS[c][1] for c in checks]
    bw = 13 + max(len(t) for t in texts) * cw
    ys = [cy + 14] if len(checks) == 1 else [cy + 6, cy + 28]
    _fits(R, ys[0] - cy - 11, ys[-1] - cy + 4, bw)
    bx = cx - bw / 2
    lines = "".join(_glyph(bx + 4.5, y - 4.5, CHECKS[c][0]) +
                    f'<text class="sub f-domains-ck" x="{f(bx + 13)}" y="{f(y)}">{escape(CHECKS[c][1])}</text>'
                    for c, y in zip(checks, ys))
    back = (f'<g class="f-domains-face f-domains-back"><path class="f-domains-bx" d="{hx}"/>'
            f'<text class="sub f-domains-ix" x="{f(cx)}" y="{f(cy - 50)}" text-anchor="middle">{idx}</text>'
            f'<text class="hdr f-domains-bn" x="{f(cx)}" y="{f(cy - 20)}" text-anchor="middle">{escape(name.upper())}</text>'
            f'<path class="f-domains-rule" d="M{f(cx - 24)},{f(cy - 9)} h48"/>{lines}</g>')
    return (f'<g class="f-domains-tile" tabindex="0" role="img" aria-label="{escape(_tile_label(name, checks))}" '
            f'data-flip="0" data-i="{idx}" data-t="{_tv(dt)}">'
            f'<path class="f-domains-hit" d="{hx}"/>{front}{back}'
            f'<path class="f-domains-ping" d="{_hex(cx, cy, R + 3.5)}" opacity="0"/>'
            f'<path class="f-domains-ring" d="{_hex(cx, cy, R + 3.5)}"/></g><!--/tile-->')


def _panel(pre, cx, cy, R, v):
    _fits(R, -32, -20, 14 * HW[v])
    return (f'<g class="f-domains-pnl"><path class="panel" d="{_hex(cx, cy, R)}" style="fill:url(#{pre}-pnl)"/>'
            f'<path class="f-domains-core" d="{_hex(cx, cy, R - 7)}"/>'
            f'<text class="hdr f-domains-pm" x="{f(cx)}" y="{f(cy - 20)}" text-anchor="middle">DOMAIN PROFILE</text>'
            f'<text class="sub f-domains-pi" x="{f(cx)}" y="{f(cy + 6)}" text-anchor="middle">&quot;checks&quot;: […]</text>'
            f'<text class="sub f-domains-pm" x="{f(cx)}" y="{f(cy + 28)}" text-anchor="middle">one per domain</text>'
            f'<path class="f-domains-pp" d="{_hex(cx, cy, R + 3.5)}" opacity="0"/></g>')


def _lattice(pre, rows, panel_at, cx, y0, R, g, v):
    """rows: tiles per row (offset honeycomb, pointy-top); panel_at: (row, k) of the profile. Returns markup, bottom y."""
    W = SQ3 * R + g  # centre pitch
    vp = W * SQ3 / 2
    sites = []
    for r, n in enumerate(rows):
        for k in range(n):
            sites.append(((r, k), cx + (k - (n - 1) / 2) * W, y0 + r * vp))
    pc = next((x, y) for rk, x, y in sites if rk == panel_at)
    tiles = [(x, y) for rk, x, y in sites if rk != panel_at]
    assert len(tiles) == 10
    speed = W / WAVE_S
    dist = [math.hypot(x - pc[0], y - pc[1]) for x, y in tiles]
    dts = [(d - R) / speed for d in dist]
    back = max(dts) + HOLD_BACKS
    r0, r1 = R, max(dist) + W / SQ3 + 12
    mask = (f'<mask id="{pre}-seam" maskUnits="userSpaceOnUse">'
            f'<path fill="#fff" d="{"".join(_hex(x, y, W / SQ3) for _, x, y in sites)}"/>'
            f'<path fill="#000" d="{"".join(_hex(x, y, R) for _, x, y in sites)}"/></mask>')
    waves = "".join(f'<circle class="f-domains-wave" cx="{f(pc[0])}" cy="{f(pc[1])}" r="{f(r0)}" opacity="0" '
                    f'mask="url(#{pre}-seam)" data-t="{_tv(t)}" data-r0="{f(r0)}" data-r1="{f(r1)}" '
                    f'data-d="{_tv((r1 - r0) / speed)}"/>' for t in (0, back))
    body = (mask + _panel(pre, pc[0], pc[1], R, v) + "".join(_tile(i, x, y, R, dts[i], v) for i, (x, y) in enumerate(tiles))
            + waves)
    return body, y0 + (len(rows) - 1) * vp + R


def _key(x0, y, w, v):
    """The six checks: hard group, soft group; each row lists the domains (pips) whose profile names it."""
    P = [hdr(x0, y, "SIX CHECKS")]
    cw, users = CW[v], {c: [i for i, d in enumerate(DOMAINS) if c in d[2]] for c in CHECKS}
    assert sum(len(u) for u in users.values()) == 15
    y += 40
    for hard, title in ((True, "HARD · A FAIL REJECTS"), (False, "SOFT · A FAIL LOWERS THE RANK")):
        assert 18 + len(title) * TAGW[v] <= w
        P.append(f'<g class="f-domains-kg">{_glyph(x0 + 5, y - 4.5, hard)}<text class="tag" x="{f(x0 + 18)}" y="{f(y)}">{title}</text></g>')
        y += 12
        for c, (h, _t, name, sub, _a) in CHECKS.items():
            if h != hard:
                continue
            n = len(users[c])
            px0 = x0 + w - 12 - 10.4 - 25 * (n - 1)  # leftmost pip centre
            assert x0 + 30 + len(name) * TTLW + 8 <= px0 - 10.4, name
            assert len(sub) <= 22 and x0 + 30 + len(sub) * cw <= x0 + w - 8, sub
            pips = "".join(f'<g class="f-domains-pip" data-i="{i + 1:02d}"><path class="f-domains-pb" d="{_hex(px0 + 25 * j, y + 17, 12)}"/>'
                           f'<path class="f-domains-lit" d="{_hex(px0 + 25 * j, y + 17, 12)}"/>'
                           f'<text class="sub f-domains-pn" x="{f(px0 + 25 * j)}" y="{f(y + 21.5)}" text-anchor="middle">{i + 1:02d}</text></g>'
                           for j, i in enumerate(users[c]))
            P.append(f'<g class="card f-domains-row"><rect x="{f(x0)}" y="{f(y)}" width="{f(w)}" height="54" rx="10"/>'
                     + _glyph(x0 + 16, y + 19.5, hard)
                     + f'<text class="ttl sm" x="{f(x0 + 30)}" y="{f(y + 24)}">{escape(name)}</text>'
                     f'<text class="sub" x="{f(x0 + 30)}" y="{f(y + 45)}">{escape(sub)}</text>{pips}</g>')
            y += 62
        y += 24
    P.append(f'<text class="lbl" x="{f(x0)}" y="{f(y + 2)}">pips: the domains whose profile names it</text>'
             f'<text class="lbl" x="{f(x0)}" y="{f(y + 24)}">RDKit or pymatgen not installed → unknown</text>')
    return "".join(P), y + 28


def _defs(pre):
    return (f'<defs><linearGradient id="{pre}-pnl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="f-domains-g0"/>'
            '<stop offset="1" class="f-domains-g1"/></linearGradient></defs>')


LEGEND = [("adot", "hard: a fail rejects"), ("ring", "soft: lowers the rank"), ("flow", "ripple flips the tiles"),
          ("hex", "hover or focus flips a tile")]

_USES = {c: ", ".join(d[0] if d[0] == "MOF" else d[0].lower() for d in DOMAINS if c in d[2]) for c in CHECKS}
_USES = {c: (u.rsplit(", ", 1)[0] + " and " + u.rsplit(", ", 1)[1]) if ", " in u else u for c, u in _USES.items()}
LABEL = ("Ten material domains as a honeycomb of tiles around the domain profile, which names the checks each domain runs "
         "on a hypothesis. A ripple from the profile turns each tile over to show its checks, and a check key numbers the "
         f"domains that run each check. Hard checks reject a hypothesis that fails: {CHECKS['smiles'][4]} for {_USES['smiles']}; "
         f"{CHECKS['iza'][4]} and {CHECKS['sial'][4]} for {_USES['iza']}; {CHECKS['comp'][4]} for {_USES['comp']}. "
         f"Soft checks lower its rank: {CHECKS['charge'][4]} for {_USES['charge']}; {CHECKS['radius'][4]} for {_USES['radius']}. "
         "A missing identifier, or RDKit or pymatgen not installed, gives unknown, never a failure. "
         "Hover over or focus a tile to turn it over.")
assert _USES["iza"] == _USES["sial"] == "zeolite"


def _svg(w, h, body, variant):
    # a group, not an img: the tiles are keyboard-focusable and must stay in the accessibility tree
    return svg(w, h, body, variant, LABEL, role="group", attrs='data-fig-tiles="1"')


def _wide():
    W, R, g, pre = 1100, 96, 10, "dom-w"
    lat_w = 3 * (SQ3 * R + g) + SQ3 * R
    cx = 30 + lat_w / 2
    lat, bot = _lattice(pre, [4, 3, 4], (1, 1), cx, 54 + R, R, g, "wide")
    kx = 30 + lat_w + 36
    key, kbot = _key(kx, 30, W - 28 - kx, "wide")
    assert kbot <= bot
    H = round(bot + 62)
    P = [_defs(pre), hdr(30, 30, "TEN DOMAIN PROFILES"), lat, key, legend(LEGEND, 30, H - 20)]
    return _svg(W, H, "".join(P), "wide")


def _narrow():
    W, R, g, pre = 360, 98, 10, "dom-n"
    lat, bot = _lattice(pre, [2, 1, 2, 1, 2, 1, 2], (3, 0), W / 2, 46 + R, R, g, "narrow")
    assert W / 2 + (SQ3 * R + g) / 2 + SQ3 * R / 2 + 4 <= W  # outer tiles and their focus ring stay inside
    key, kbot = _key(12, bot + 40, W - 24, "narrow")
    P = [_defs(pre), hdr(12, 24, "TEN DOMAIN PROFILES"), lat, key,
         "".join(legend([it], 12, kbot + 30 + 26 * k) for k, it in enumerate(LEGEND))]
    return _svg(W, round(kbot + 30 + 26 * 3 + 12), "".join(P), "narrow")


JS = """MAFig.register("domains", function (root, variant) {
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var tiles = q(".f-domains-tile"), waves = q(".f-domains-wave"), pp = root.querySelector(".f-domains-pp");
  var back = +waves[1].getAttribute("data-t"), last = Math.max.apply(null, tiles.map(function (t) { return +t.getAttribute("data-t"); }));
  gsap.set(q(".f-domains-lit"), {transformOrigin: "50% 50%"});
  // everything a pass reveals by opacity is registered here, and the loop clears exactly this list
  var shown = [], reg = function (x) { shown = shown.concat(x); return x; };
  // one pass from t0: a ripple leaves the profile; each tile turns over (CSS flip on data-flip) as the wave front
  // reaches it, and only then do its pips light in the key. After the hold, a second ripple turns the tiles back.
  // Every key in a fromTo start object is repeated in its end object (a loop wrap drops start-only keys).
  function pass(tl, t0) {
    waves.forEach(function (w, k) {
      var t = t0 + +w.getAttribute("data-t"), d = +w.getAttribute("data-d");
      tl.fromTo(w, {attr: {r: +w.getAttribute("data-r0")}}, {attr: {r: +w.getAttribute("data-r1")}, duration: d, ease: "none"}, t)
        .fromTo(w, {opacity: 0}, {opacity: 1, duration: .15}, t)
        .to(w, {opacity: 0, duration: .4}, t + d - .4)
        .fromTo(pp, {opacity: 0}, {opacity: 1, duration: .12}, t - .1)
        .to(pp, {opacity: 0, duration: .5}, t + .1);
      tiles.forEach(function (tile) {
        var tf = t + +tile.getAttribute("data-t"), ping = tile.querySelector(".f-domains-ping");
        tl.fromTo(ping, {opacity: 0}, {opacity: 1, duration: .1}, tf - .1)
          .to(ping, {opacity: 0, duration: .45}, tf + .05)
          .set(tile, {attr: {"data-flip": k ? 0 : 1}}, tf);
        if (!k) tl.fromTo(reg(q('.f-domains-pip[data-i="' + tile.getAttribute("data-i") + '"] .f-domains-lit')),
          {opacity: 0, scale: .3}, {opacity: 1, scale: 1, duration: .3, ease: "back.out(2.2)", stagger: .06}, tf + __PIP__);
      });
    });
  }
  var intro = gsap.timeline({defaults: {ease: "power3.out"}});
  intro.from(q(".hdr:not(.f-domains-bn):not(.f-domains-pm), .legend, .lbl"), {opacity: 0, duration: .5}, 0)
    .from(q(".f-domains-pnl"), {opacity: 0, scale: .9, transformOrigin: "50% 50%", duration: .5}, .1)
    .from(tiles, {opacity: 0, scale: .86, transformOrigin: "50% 50%", duration: .4, stagger: .05}, .25)
    .from(q(".f-domains-kg, .f-domains-row"), {opacity: 0, x: 10, duration: .35, stagger: .06}, .35);
  pass(intro, __T0I__);
  // loop: hold the finished frame (fronts up, every pip lit), clear what the pass reveals, replay. immediateRender
  // off: the frame stays until then.
  var loop = gsap.timeline({repeat: -1, defaults: {immediateRender: false}});
  loop.to(shown, {opacity: 0, duration: .4}, __HOLD__);
  pass(loop, __T0L__);
  loop.set({}, {}, __T0L__ + back + last + .9);
  return {intro: intro, loop: loop};
});"""
for _k, _v in {"__PIP__": PIP_LAG, "__T0I__": T0_INTRO, "__HOLD__": HOLD, "__T0L__": T0_LOOP}.items():
    JS = JS.replace(_k, _tv(_v))
assert "__" not in JS


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
