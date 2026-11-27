"""Shared SVG helpers for the figure generator; classes match the CSS family in index.html."""
import math
from dataclasses import dataclass
from html import escape


@dataclass
class Figure:
    """One figure: wide and narrow <svg> markup plus its MAFig.register(...) script."""
    wide: str
    narrow: str
    js: str


def f(x):
    return f"{x:.1f}"


def hexpath(cx, cy, r):
    """Pointy-top hexagon path centred on (cx, cy) with circumradius r."""
    pts = [(cx + r * math.cos(math.radians(-90 + 60 * k)), cy + r * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + " Z"


ICONS = {
    "search": '<circle cx="7.5" cy="7.5" r="5"/><path d="m11.3 11.3 4.2 4.2"/>',
    "augment": '<rect x="2.5" y="2" width="9" height="12" rx="1.5"/><path d="M5 5.5h4M5 8h4M5 10.5h2.5"/><path d="m13 6 2.5 2.5L13 11"/>',
    "plan": '<path d="M3 4h12M3 9h8M3 14h10"/><circle cx="15" cy="9" r="1.6"/>',
    "discover": '<path d="m6 5-3.5 4L6 13M12 5l3.5 4L12 13M10 3.5 8 14.5"/>',
    "evaluate": '<path d="M3 15V9M7.5 15V5M12 15v-7M16 15V3"/>',
    "memory": '<ellipse cx="9" cy="4.2" rx="5.6" ry="2.1"/><path d="M3.4 4.2v9.4c0 1.2 2.5 2.1 5.6 2.1s5.6-.9 5.6-2.1V4.2M3.4 8.9c0 1.2 2.5 2.1 5.6 2.1s5.6-.9 5.6-2.1"/>',
    "chat": '<path d="M3 3.5h12a1.5 1.5 0 0 1 1.5 1.5v6A1.5 1.5 0 0 1 15 12.5H8l-3.5 3v-3H3A1.5 1.5 0 0 1 1.5 11V5A1.5 1.5 0 0 1 3 3.5z"/>',
    "chain": '<rect x="1.5" y="6" width="5" height="5" rx="1.2"/><rect x="11.5" y="6" width="5" height="5" rx="1.2"/><path d="M6.5 8.5h5"/>',
    "plug": '<path d="M6.5 2v4M11.5 2v4M4 6h10v3.5a5 5 0 0 1-10 0zM9 14.5V17"/>',
}

# Hidden shared defs: one <symbol id="i-<name>"> per icon (18x18), the hexagon (r = 10) and the tick, and the arrowhead.
SYMBOLS = (
    "".join(f'<symbol id="i-{n}" viewBox="0 0 18 18" width="18" height="18" overflow="visible">{d}</symbol>' for n, d in ICONS.items())
    + f'<symbol id="hex" viewBox="-10 -10 20 20" width="20" height="20" overflow="visible"><path d="{hexpath(0, 0, 10)}" vector-effect="non-scaling-stroke"/></symbol>'
    + '<symbol id="chk" viewBox="0 0 12 12" width="12" height="12" overflow="visible"><path d="M2.5 6.4 5 8.8 9.6 3.4"/></symbol>'
    + '<marker id="arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
    '<path d="M0,0 L8,4 L0,8 z" fill="var(--line-strong)"/></marker>'
)


def icon(name, x, y, cls="ic"):
    if name not in ICONS:
        raise KeyError(f"unknown icon {name!r}")
    return f'<use class="{cls}" href="#i-{name}" x="{f(x)}" y="{f(y)}"/>'


def hexuse(cx, cy, r, cls="hx"):
    """<use> of #hex centred on (cx, cy) with circumradius r; always emits explicit width/height (the symbol alone would fill the host SVG)."""
    return f'<use class="{cls}" href="#hex" x="{f(cx - r)}" y="{f(cy - r)}" width="{f(2 * r)}" height="{f(2 * r)}"/>'


def card(x, y, w, h, title, sub="", cls=""):
    c = f"card {cls}".strip()
    s = f'<text class="sub" x="{f(x + 14)}" y="{f(y + 43)}">{escape(sub)}</text>' if sub else ""
    return (f'<g class="{c}"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
            f'<text class="ttl" x="{f(x + 14)}" y="{f(y + 24)}">{escape(title)}</text>{s}</g>')


def curve_d(x1, y1, x2, y2):
    """Path data of a horizontal-tangent cubic Bezier from (x1, y1) to (x2, y2)."""
    dx = max(abs(x2 - x1) * 0.5, 12) * (1 if x2 >= x1 else -1)
    return f"M{f(x1)},{f(y1)} C{f(x1 + dx)},{f(y1)} {f(x2 - dx)},{f(y2)} {f(x2)},{f(y2)}"


def curve(x1, y1, x2, y2, cls="cv", arrow=True, attrs=""):
    """<path> of curve_d; attrs is extra raw attribute text, e.g. 'opacity="0"'."""
    m = ' marker-end="url(#arr)"' if arrow else ""
    a = f" {attrs}" if attrs else ""
    return f'<path class="{cls}" d="{curve_d(x1, y1, x2, y2)}"{m}{a}/>'


def hdr(x, y, text, anchor="start"):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return f'<text class="hdr" x="{f(x)}" y="{f(y)}"{a}>{escape(text)}</text>'


def flathex(cx, cy, r):
    """Flat-top hexagon path centred on (cx, cy) with circumradius r."""
    pts = [(cx + r * math.cos(math.radians(60 * k)), cy + r * math.sin(math.radians(60 * k))) for k in range(6)]
    return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts) + " Z"


_SWATCH = {
    "flow": lambda x: f'<path d="M{x},-4 h22" class="lg-flow"/>',
    "amber": lambda x: f'<path d="M{x},-4 h22" class="lg-amber"/>',
    "dot": lambda x: f'<circle cx="{x + 4}" cy="-4" r="4" class="lg-dot"/>',
    "dash": lambda x: f'<path d="M{x},-4 h22" class="lg-dash"/>',
    "hex": lambda x: f'<path d="{flathex(x + 11, -4, 8)}" class="lg-hex"/>',
    "hexdash": lambda x: f'<path d="{flathex(x + 11, -4, 8)}" class="lg-hexdash"/>',
    "tick": lambda x: f'<rect x="{x + 2}" y="-13" width="18" height="18" rx="4" class="lg-box"/><path d="M{x + 6.5},-4.5 l3.5,3.5 l6,-7" class="lg-tick"/>',
    "cell": lambda x: f'<rect x="{x + 2}" y="-13" width="18" height="18" rx="4" class="lg-cell"/>',
}


def legend(items, x, y):
    """Legend row of (swatch_kind, text); advances by an estimated text width (13.4-unit mono ~ 8.1 units/char)."""
    out, cx = [], 0
    for kind, text in items:
        out.append(_SWATCH[kind](cx) + f'<text x="{cx + 30}" y="0">{escape(text)}</text>')
        cx += 30 + int(len(text) * 8.1) + 22
    return f'<g class="legend" transform="translate({f(x)},{f(y)})">{"".join(out)}</g>'


def note(x, y, text="values are illustrative"):
    """A legend-row note with no swatch."""
    return f'<g class="legend" transform="translate({f(x)},{f(y)})"><text x="0" y="0">{escape(text)}</text></g>'


def svg(w, h, body, variant, label):
    if variant not in ("wide", "narrow"):
        raise ValueError(variant)
    return f'<svg class="sch {variant}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">{body}</svg>'
