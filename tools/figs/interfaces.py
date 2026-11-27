"""Interfaces figure: the database as a radial hub (claims C33-C36, C50, C73-C75).
Six sources sit on an outer orbit; each sends records inward along curved orbital lanes through concentric shells:
the mapping ring, one gate centred on each source (a fixed template for a known source-database pair, a language model for uploads and any other pair,
KC extraction for records from papers), the review shell (a person reviews the column mapping of a Data Agent import;
KC records skip it), the check shell, and the dark database core, where each record docks into a slot. Chat and the MCP
server are two ports under the hub: an import started from either waits until a person confirms it (chat's upload,
an MCP agent's Open Catalyst import), and at the end both ports read from the database. A record docks only after it is mapped, reviewed and checked; the order
is fixed in data-e/data-t here and asserted at build time and in the tests. Two records per source; values are
illustrative."""
import math
from html import escape

from figkit import Figure, f, hdr, icon, legend, note, svg, vcurve_d

CLAIMS = ("C33", "C34", "C35", "C36", "C50", "C73", "C74", "C75")  # register rows this figure's text and aria-label rest on

# (title, detail, how it is mapped, icon, mapping kind, orbit angle in degrees, clockwise from +x), in launch order
SRC = [("Uploads", "CSV, JSON, Excel", "language model", "upload", "lm", 135),
       ("Materials Project", "needs an API key", "template → CatPlat", "dm-ceramic", "tpl", 180),
       ("MPEA alloys", "Citrine dataset", "template → metal", "dm-metal", "tpl", 225),
       ("PolyMetriX", "polymer Tg dataset", "template → polymer", "dm-polymer", "tpl", 270),
       ("Papers", "KC 6.1–6.4", "records extracted", "augment", "kc", 315),
       ("Open Catalyst", "download or local", "template → CatPlat", "dm-catalyst", "tpl", 0)]
I_CHAT, I_MCP = 0, 5  # chat starts the upload; an MCP agent starts the Open Catalyst import
# Each source's two lanes fan out almost radially to its own gate (offsets O at the ring, centred on the source), then
# turn inside the ring to their slots (E): every gate, review mark and check tick sits by the source it belongs to.
O_GATE, E_SLOT = (-4, 4), (0, 15)
NSLOT = 24  # slots every 15 degrees, so every lane ends on one
for _s in SRC:
    assert len(_s[1]) <= 22 and len(_s[2]) <= 22 and _s[5] % 45 == 0, _s
assert all((a + e) % (360 // NSLOT) == 0 for *_, a in SRC for e in E_SLOT) and max(E_SLOT) - min(O_GATE) < 45 / 2

CW = {"wide": 7.68, "narrow": 8.04}  # Geist Mono advance per character at the sub size
HW = {"wide": 9.73, "narrow": 10.18}  # header advance (0.6 em + .16 em letter-spacing)

# radii: orbit, mapping ring (inner, outer), review shell, check shell, core, slot ring; planet and slot radius
G = {"wide": dict(W=1100, cx=550, cy=395, orb=262, m0=162, m1=186, rev=142, chk=122, core=100, slot=86, pr=21, sr=4.5),
     "narrow": dict(W=360, cx=180, cy=632, orb=162, m0=118, m1=136, rev=106, chk=85, core=72, slot=62, pr=16, sr=3.8)}

# --- timing (s) within one pass -----------------------------------------------------------------------------------
# a port pulses (asked to import), its chip waits for a person, the tick shows, then the request reaches the source
T_CHAT, T_CCWAIT, T_CCONF = (0.0, .5), (.5, 1.1), 1.1
T_MCP, T_CWAIT, T_CONF = (2.3, 2.9), (2.9, 3.5), 3.5
L = [1.6, .4, .9, 2.1, 2.6, 3.7]  # each source lights and launches its two records
TO_GATE, TO_REV, REV_D, DOCK_D = .8, .25, .65, .5
T0_INTRO, HOLD, T0_LOOP = 1.4, 1.2, 1.8


def _tv(t):
    return f"{t:.2f}".rstrip("0").rstrip(".")


def _at(e, t, i=None, extra=""):
    """Reveal attributes: data-e names the event (tests check its order), data-t its time in a pass, data-i the source."""
    s = f'data-e="{e}" data-t="{_tv(t)}"' + (f' data-i="{i}"' if i is not None else "")
    return s + (f" {extra}" if extra else "")


def _ease_inv(q):
    """Time share at which power1.inOut has covered share q of a move."""
    return math.sqrt(q / 2) if q < .5 else 1 - math.sqrt((1 - q) / 2)


def _schedule():
    """Per source: lane moves (start, duration, head %) per record, and the event times. Heads come from _lane."""
    ev = []
    for i, s in enumerate(SRC):
        t, kc = L[i], s[4] == "kc"
        rec = []
        for k in range(2):
            t0 = t + .1 + .2 * k
            tg = t0 + TO_GATE
            if kc:
                rec.append([(t0, TO_GATE, "g"), (tg + .1, DOCK_D + .05, 100)])
            else:
                rel = t + 1.4 + REV_D + .1 * k
                rec.append([(t0, TO_GATE, "g"), (tg + .05, TO_REV, "r"), (rel, DOCK_D, 100)])
        e = {"lit": t, "map": t + .1 + TO_GATE}
        if not kc:
            e["wait"], e["rev"] = (t + 1.4, t + 1.4 + REV_D), t + 1.4 + REV_D
        ev.append((rec, e))
    return ev


SCHED = _schedule()


def _pt(g, r, a):
    a = math.radians(a)
    return g["cx"] + r * math.cos(a), g["cy"] + r * math.sin(a)


def _arc(g, r, a0, a1):
    x0, y0 = _pt(g, r, a0)
    x1, y1 = _pt(g, r, a1)
    big = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{f(x0)},{f(y0)} A{r},{r} 0 {big} 1 {f(x1)},{f(y1)}"


def _band(g, r0, r1, a0, a1):
    """Closed annulus sector between radii r0 < r1 from a0 to a1 (clockwise)."""
    x0, y0 = _pt(g, r1, a0)
    x1, y1 = _pt(g, r1, a1)
    x2, y2 = _pt(g, r0, a1)
    x3, y3 = _pt(g, r0, a0)
    big = 1 if (a1 - a0) % 360 > 180 else 0
    return (f"M{f(x0)},{f(y0)} A{r1},{r1} 0 {big} 1 {f(x1)},{f(y1)} L{f(x2)},{f(y2)} "
            f"A{r0},{r0} 0 {big} 0 {f(x3)},{f(y3)} Z")


def _ang(g, a, k, r):
    """Angle of lane k of the source at a, at radius r: a slight fan to the gate, then a smooth turn to the slot."""
    if r >= g["m1"]:
        return a + O_GATE[k] * (g["orb"] - r) / (g["orb"] - g["m1"])
    s = (g["m1"] - r) / (g["m1"] - g["slot"])
    return a + O_GATE[k] + (E_SLOT[k] - O_GATE[k]) * s * s * (3 - 2 * s)


def _lane(g, a, k):
    """One lane from the source on the orbit to its slot, as Catmull-Rom cubics.
    Returns the path data and a function giving the share of its length (%) at which it first reaches radius R."""
    n = 10
    P = [_pt(g, r, _ang(g, a, k, r)) for r in (g["orb"] - u / n * (g["orb"] - g["slot"]) for u in range(n + 1))]
    E = [P[0]] + P + [P[-1]]
    segs = []
    for j in range(1, n + 1):
        p0, p1, p2, p3 = E[j - 1], E[j], E[j + 1], E[j + 2]
        segs.append((p1, (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6),
                     (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6), p2))
    d = f"M{f(P[0][0])},{f(P[0][1])} " + " ".join(f"C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(q[0])},{f(q[1])}"
                                                    for _p, c1, c2, q in segs)
    pts = []
    for p, c1, c2, q in segs:
        for m in range(40):
            t = m / 40
            w = ((1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3)
            pts.append((sum(wi * v[0] for wi, v in zip(w, (p, c1, c2, q))), sum(wi * v[1] for wi, v in zip(w, (p, c1, c2, q)))))
    pts.append(P[-1])
    cum = [0]
    for a_, b_ in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(b_[0] - a_[0], b_[1] - a_[1]))
    total = cum[-1]

    def at(R):
        for (x, y), c in zip(pts, cum):
            if math.hypot(x - g["cx"], y - g["cy"]) <= R:
                return 100 * c / total
        raise ValueError(R)
    return d, total, at


def _lanes(g):
    """Per source and record: path data, segment share, moves with numeric heads, check-crossing time, dock time."""
    out = []
    for i, s in enumerate(SRC):
        rec, e = SCHED[i]
        lanes = []
        for k in range(2):
            d, total, at = _lane(g, s[5], k)
            heads = {"g": at((g["m0"] + g["m1"]) / 2), "r": at(g["rev"] + 3), 100: 100}
            moves = [(t, du, heads[h]) for t, du, h in rec[k]]
            sl = 100 * 16 / total
            t, du, h = moves[-1]
            h0 = moves[-2][2]
            tc = t + du * _ease_inv((at(g["chk"]) - h0) / (h - h0))
            lanes.append(dict(d=d, sl=sl, moves=moves, tc=tc, td=t + du))
            assert moves[0][2] > sl and all(a[0] + a[1] <= b[0] + 1e-9 for a, b in zip(moves, moves[1:]))
        out.append(lanes)
    return out


def _events(lanes):
    """Event times of one pass, from the schedule and the lane geometry (the check tick follows the first record)."""
    E = []
    for i, s in enumerate(SRC):
        _rec, e = SCHED[i]
        ln = lanes[i]
        E.append(dict(e, chk=min(x["tc"] for x in ln) + .03, dock=[x["td"] for x in ln]))
    t_count = max(t for e in E for t in e["dock"]) + .2
    return E, t_count, t_count + .3


def _check_order(E, t_count, t_q):
    for i, e in enumerate(E):
        kc = SRC[i][4] == "kc"
        seq = [e["lit"], e["map"]] + ([] if kc else [e["wait"][0], e["rev"]]) + [e["chk"], min(e["dock"])]
        assert all(a < b for a, b in zip(seq, seq[1:])), (i, seq)
        if not kc:
            assert e["wait"][0] > e["map"] + .3 and e["wait"][1] <= e["rev"]  # pauses once mapped; passes when reviewed
    assert T_CHAT[0] < T_CCWAIT[0] < T_CCONF < L[I_CHAT] and T_MCP[0] < T_CWAIT[0] < T_CONF < L[I_MCP]
    assert max(max(e["dock"]) for e in E) < t_count < t_q


def _defs(pre):
    return (f'<defs><radialGradient id="{pre}-pnl" cx="50%" cy="42%" r="60%"><stop offset="0" class="f-interfaces-g0"/>'
            f'<stop offset="1" class="f-interfaces-g1"/></radialGradient></defs>')


def _gaps(g, v):
    """Half-angles of the label breaks at the bottom of the check shell, review shell and mapping ring."""
    def half(r, txt):
        return math.degrees(math.asin((len(txt) * HW[v] / 2 + 7) / r))
    return half(g["chk"], "CHECK"), half(g["rev"], "REVIEW"), half((g["m0"] + g["m1"]) / 2, "MAP")


def _hub(g, v, pre, lanes, E):
    """Orbit, mapping ring with its gates, review and check shells, the core with its slots, lanes and records."""
    cx, cy, P = g["cx"], g["cy"], []
    gc, gr, gm = _gaps(g, v)
    mid = (g["m0"] + g["m1"]) / 2
    P.append(f'<circle class="f-interfaces-orbit" cx="{cx}" cy="{cy}" r="{g["orb"]}" pathLength="360" data-o="{cx} {cy}"/>')
    # lanes (static, faint) under everything else
    P.append('<g class="f-interfaces-lanes">' + "".join(f'<path d="{x["d"]}"/>' for ln in lanes for x in ln) + "</g>")
    # mapping ring: a faint base band, broken at the bottom for its label, and one gate per source
    P.append(f'<path class="f-interfaces-ring" d="{_band(g, g["m0"], g["m1"], 90 + gm, 450 - gm)}"/>')
    for i, s in enumerate(SRC):
        a, kind = s[5], s[4]
        a0, a1 = _ang(g, a, 0, mid) - 6, _ang(g, a, 1, mid) + 6
        body = f'<path class="f-interfaces-gb" d="{_band(g, g["m0"], g["m1"], a0, a1)}"/>'
        if kind == "tpl":  # a fixed comb: column to column
            body += '<path class="f-interfaces-comb" d="' + " ".join(
                "M{0},{1} L{2},{3}".format(*map(f, _pt(g, g["m0"] + 3, b) + _pt(g, g["m1"] - 3, b)))
                for b in [a0 + 3 + j * (a1 - a0 - 6) / 5 for j in range(6)]) + '"/>'
        elif kind == "lm":  # scattered: a model decides
            for j, (fr, rr) in enumerate([(.15, .3), (.35, .7), (.55, .25), (.7, .6), (.88, .4)]):
                x, y = _pt(g, g["m0"] + rr * (g["m1"] - g["m0"]), a0 + fr * (a1 - a0))
                body += f'<circle class="f-interfaces-lmd" cx="{f(x)}" cy="{f(y)}" r="2"/>'
        else:  # KC: records lifted out of the text
            body += f'<path class="f-interfaces-kcl" d="{_arc(g, g["m0"] + 7, a0 + 2, a1 - 2)} {_arc(g, g["m1"] - 7, a0 + 2, a1 - 2)}"/>'
        ev, t = ("xtr" if kind == "kc" else "map"), E[i]["map"]
        P.append(f'<g class="f-interfaces-gate {kind}" data-a="{a}" data-ga="{(a0 + a1) / 2:.1f}">{body}</g>'
                 f'<path class="f-interfaces-glit" d="{_band(g, g["m0"], g["m1"], a0, a1)}" {_at(ev, t, i)}/>')
    # review shell: amber, dashed; no arc where KC records pass (they have no mapping to review)
    kc = next(s[5] for s in SRC if s[4] == "kc")
    k0, k1 = _ang(g, kc, 0, g["rev"]) - 8, _ang(g, kc, 1, g["rev"]) + 8
    P.append(f'<path class="f-interfaces-rev" d="{_arc(g, g["rev"], 90 + gr, k0)} {_arc(g, g["rev"], k1, 450 - gr)}"/>')
    P.append(f'<path class="f-interfaces-chk" d="{_arc(g, g["chk"], 90 + gc, 450 - gc)}"/>')
    # core: the one dark panel, with the slot ring
    P.append(f'<circle class="panel f-interfaces-core" cx="{cx}" cy="{cy}" r="{g["core"]}" style="fill:url(#{pre}-pnl)"/>')
    P.append('<g class="f-interfaces-slots">' + "".join(
        '<circle cx="{0}" cy="{1}" r="{2}"/>'.format(*map(f, _pt(g, g["slot"], j * 360 / NSLOT)), g["sr"]) for j in range(NSLOT)) + "</g>")
    # per-source shell marks: review wait (amber) then passed (teal), the check tick, the docked slots
    for i, s in enumerate(SRC):
        a, e = s[5], E[i]
        if s[4] != "kc":
            r0, r1 = _ang(g, a, 0, g["rev"]) - 4, _ang(g, a, 1, g["rev"]) + 4
            w = f'data-w="{_tv(e["wait"][0])} {_tv(e["wait"][1])}"'
            P.append(f'<path class="f-interfaces-wait" d="{_arc(g, g["rev"], r0, r1)}" {_at("wait", e["wait"][0], i, w)} opacity="0"/>'
                     f'<path class="f-interfaces-ok" d="{_arc(g, g["rev"], r0, r1)}" {_at("rev", e["rev"], i)}/>')
        bx, by = _pt(g, g["chk"], (_ang(g, a, 0, g["chk"]) + _ang(g, a, 1, g["chk"])) / 2)
        P.append(f'<g class="f-interfaces-ck" {_at("chk", e["chk"], i)}><circle cx="{f(bx)}" cy="{f(by)}" r="7"/>'
                 f'<path d="M{f(bx - 3.2)},{f(by + .2)} l2.2,2.3 l4.2,-4.8"/></g>')
        for k in range(2):
            x, y = _pt(g, g["slot"], a + E_SLOT[k])
            P.append(f'<circle class="f-interfaces-fill" cx="{f(x)}" cy="{f(y)}" r="{g["sr"] + .6}" {_at("dock", e["dock"][k], i)}/>')
    # records in flight
    for i, ln in enumerate(lanes):
        for x in ln:
            m = " ".join(f"{_tv(t)} {_tv(du)} {h:.1f}" for t, du, h in x["moves"])
            P.append(f'<path class="f-interfaces-pk" d="{x["d"]}" data-m="{m}" data-sl="{x["sl"]:.1f}" opacity="0"/>')
    return "".join(P)


def _inline(g, v):
    """Shell names written into the breaks at the bottom of each shell, like contour labels."""
    cx, cy, P = g["cx"], g["cy"], []
    for txt, r, cls in (("CHECK", g["chk"], ""), ("REVIEW", g["rev"], " f-interfaces-amb"), ("MAP", (g["m0"] + g["m1"]) / 2, "")):
        P.append(f'<text class="hdr{cls}" x="{cx}" y="{f(cy + r + 4.5)}" text-anchor="middle">{txt}</text>')
    return "".join(P)


def _planet(g, i, v, labelled):
    title, det, how, ic, kind, a = SRC[i]
    x, y = _pt(g, g["orb"], a)
    pr, isz = g["pr"], (18 if v == "wide" else 15)
    P = [f'<g class="f-interfaces-src" data-k="{kind}"><circle class="f-interfaces-pl" cx="{f(x)}" cy="{f(y)}" r="{pr}"/>'
         f'<use class="ic" href="#i-{ic}" x="{f(x - isz / 2)}" y="{f(y - isz / 2)}" width="{isz}" height="{isz}"/>'
         f'<circle class="f-interfaces-lit" cx="{f(x)}" cy="{f(y)}" r="{pr + 4.5}" {_at("lit", L[i], i)}/>']
    if labelled:
        if a == 270:  # above the planet
            ys, anchor, lx = (y - pr - 50, y - pr - 31, y - pr - 13), "middle", x
        else:
            right = a < 90 or a > 270
            lx, anchor = (x + pr + 12, "start") if right else (x - pr - 12, "end")
            ys = (y - 14, y + 5, y + 23)
        a_ = f' text-anchor="{anchor}"' if anchor != "start" else ""
        P.append(f'<text class="ttl" x="{f(lx)}" y="{f(ys[0])}"{a_}>{escape(title)}</text>'
                 f'<text class="sub" x="{f(lx)}" y="{f(ys[1])}"{a_}>{escape(det)}</text>'
                 f'<text class="sub f-interfaces-how {kind}" x="{f(lx)}" y="{f(ys[2])}"{a_}>{escape(how)}</text>')
    return "".join(P) + "</g>"


def _port(x, y, w, h, ic, title, subs, ev, extra=""):
    """A port card: icon, title, sub-labels, and a glow that pulses when the port is used."""
    s = "".join(f'<text class="sub" x="{f(x + 14)}" y="{f(y + 45 + 18 * j)}">{escape(t)}</text>' for j, t in enumerate(subs))
    return (f'<g class="f-interfaces-port"><rect class="f-interfaces-pc" x="{f(x)}" y="{f(y)}" width="{w}" height="{h}" rx="10"/>'
            f'{icon(ic, x + w - 32, y + 12)}<text class="ttl" x="{f(x + 14)}" y="{f(y + 25)}">{escape(title)}</text>{s}</g>'
            f'<rect class="f-interfaces-glow" x="{f(x - 3)}" y="{f(y - 3)}" width="{w + 6}" height="{h + 6}" rx="12" {ev}{extra} opacity="0"/>')


def _chip(x, y, v, t_wait, t_conf, src):
    """Imports write data, so they wait for a person: the chip's amber ring shows the wait, a tick its confirmation;
    src is the source the confirmed request starts."""
    txt = "a person confirms"
    w = 30 + len(txt) * CW[v] + 12
    wait = _at("cwait", t_wait[0], None, f'data-s="{src}" data-w="{_tv(t_wait[0])} {_tv(t_wait[1])}"')
    conf = _at("conf", t_conf, None, f'data-s="{src}"')
    return (f'<g class="f-interfaces-chip"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="26" rx="13"/>'
            f'<text class="sub" x="{f(x + 30)}" y="{f(y + 17.5)}">{txt}</text></g>'
            f'<rect class="f-interfaces-cw" x="{f(x - 3)}" y="{f(y - 3)}" width="{f(w + 6)}" height="32" rx="16" '
            f'{wait} opacity="0"/>'
            f'<circle class="f-interfaces-cdot" cx="{f(x + 14)}" cy="{f(y + 13)}" r="5"/>'
            f'<g class="f-interfaces-ck" {conf}>'
            f'<circle cx="{f(x + 14)}" cy="{f(y + 13)}" r="7"/><path d="M{f(x + 10.8)},{f(y + 13.2)} l2.2,2.3 l4.2,-4.8"/></g>')


def _pk(d, t0, du, ev):
    """A packet along a connector or conduit, start to end."""
    return f'<path class="f-interfaces-cpk" d="{d}" data-m="{_tv(t0)} {_tv(du)} 100" data-sl="18" {ev} opacity="0"/>'


LEGEND = [("flow", "record in flight"), ("amber", "waits for a person"), ("okc", "check passed"), ("dot", "docked record")]
LABEL = ("MatAgent's database drawn as a hub. Six sources sit on an orbit: Materials Project (needs an API key), the "
         "Citrine MPEA alloy dataset, the PolyMetriX polymer glass-transition dataset, Open Catalyst Project data "
         "(downloaded or from local files), CSV, JSON or Excel uploads, and papers, from which the KC modes extract "
         "records. Records stream inward along curved lanes through shells. The mapping ring: a fixed template for a "
         "known source–database pair (Materials Project and Open Catalyst into CatPlat, MPEA into the metal domain, "
         "PolyMetriX into the polymer domain), a language model for uploads and any other pair, and extraction for "
         "papers. Each Data Agent import then pauses until a person reviews its column mapping; KC records are staged "
         "instead. Records are checked (required fields, ranges), and only then dock in the CatPlat or MatPlat database. Two "
         "ports sit under the hub: chat, which starts imports and takes uploads up to 50 MiB, and answers in typed blocks "
         "with 3D structures; and the MCP server, with ten tools over stdio or SSE on localhost and per-agent tokens. An "
         "import writes data, so a person confirms it first: in chat, and for an MCP agent unless it is trusted for "
         "writes. Both "
         "ports then query the database. Two records per source; values are illustrative.")


def _glyph(x, y, w, h, kind):
    """A mapping-gate swatch: comb (template), scattered dots (language model) or stripes (KC extraction)."""
    sw = f'<rect class="f-interfaces-gb" x="{f(x)}" y="{f(y)}" width="{w}" height="{h}" rx="3"/>'
    if kind == "tpl":
        sw += '<path class="f-interfaces-comb" d="' + " ".join(f"M{f(x + w * (q + 1) / 6)},{f(y + 3)} V{f(y + h - 3)}" for q in range(5)) + '"/>'
    elif kind == "lm":
        sw += "".join(f'<circle class="f-interfaces-lmd" cx="{f(x + w * px)}" cy="{f(y + h * py)}" r="2"/>'
                      for px, py in ((.23, .25), (.47, .7), (.7, .35), (.83, .75)))
    else:
        sw += f'<path class="f-interfaces-kcl" d="M{f(x + 4)},{f(y + h * .3)} H{f(x + w - 4)} M{f(x + 4)},{f(y + h * .7)} H{f(x + w - 4)}"/>'
    return f'<g class="f-interfaces-gate {kind}">{sw}</g>'


def _keys(v):
    """Wide only: the path a record takes (top left) and the three kinds of mapping gate (top right)."""
    P = [hdr(30, 30, "RECORD PATH, INWARD")]
    for j, (tag, sub, cls) in enumerate((("01 MAP", "columns to the schema", ""), ("02 REVIEW", "a person, per import", " f-interfaces-amb"),
                                         ("03 CHECK", "fields and ranges", ""), ("04 DOCK", "records written", ""))):
        y = 58 + 23 * j
        P.append(f'<text class="hdr{cls}" x="30" y="{y}">{tag}</text><text class="sub" x="128" y="{y}">{sub}</text>')
    x0 = 846
    P.append(hdr(x0, 30, "MAPPING RING"))
    for j, (kind, ttl, sub) in enumerate((("tpl", "Fixed template", "known source–DB pair"), ("lm", "Language model", "uploads, other pairs"),
                                          ("kc", "KC extraction", "records from papers"))):
        y = 46 + 42 * j
        P.append(_glyph(x0, y + 4, 30, 20, kind) + f'<text class="ttl sm" x="{x0 + 42}" y="{y + 12}">{ttl}</text>'
                 f'<text class="sub" x="{x0 + 42}" y="{y + 31}">{sub}</text>')
    return "".join(P)


def _core_text(g, v, t_count):
    cx, cy = g["cx"], g["cy"]
    if v == "wide":
        rows = [("hdr f-interfaces-pm", cy - 20, "DATABASE"), ("sub f-interfaces-pi", cy + 2, "CatPlat · MatPlat")]
        yc = cy + 26
    else:
        rows = [("hdr f-interfaces-pm", cy - 25, "DATABASE"), ("sub f-interfaces-pi", cy - 5, "CatPlat"), ("sub f-interfaces-pi", cy + 13, "MatPlat")]
        yc = cy + 34
    out = "".join(f'<text class="{c}" x="{cx}" y="{f(y)}" text-anchor="middle">{t}</text>' for c, y, t in rows)
    return out + f'<text class="sub f-interfaces-cnt" x="{cx}" y="{f(yc)}" text-anchor="middle" {_at("count", t_count)}>+12 records</text>'


def _ports(g, v, t_q):
    """Chat and MCP cards under the hub, their conduits to the core, and their connectors to the sources they start."""
    cx, cy = g["cx"], g["cy"]
    ux, uy = _pt(g, g["orb"], SRC[I_CHAT][5])
    ox, oy = _pt(g, g["orb"], SRC[I_MCP][5])
    pr = g["pr"]
    if v == "wide":
        cy0, w, h = 690, 230, 92
        chat, mcp = (290, cy0), (580, cy0)
        subs_m = ("ten tools", "stdio or localhost SSE", "per-agent tokens")
        ca, ma = 112, 68
        con_c = vcurve_d(350, cy0, ux, uy + pr + 2)
        con_m = vcurve_d(780, cy0, ox, oy + pr + 2)
        chips = ((170, 620), (800, 620), (806, 663, "start"))
    else:
        cy0, w, h = 818, 160, 92
        chat, mcp = (12, cy0), (188, cy0)
        subs_m = ("ten tools", "stdio · local SSE", "per-agent tokens")
        ca, ma = 115, 65
        con_c = vcurve_d(ux, cy0, ux, uy + pr + 2)
        con_m = vcurve_d(ox - 8, cy0, ox, oy + pr + 2)
        cw_ = 30 + 17 * CW[v] + 12
        chips = ((12, cy0 + h + 12), (348 - cw_, cy0 + h + 48), (348, cy0 + h + 48 + 44, "end"))
    t0, t1 = T_CHAT
    qa = f"{_tv(t_q + .5)} {_tv(t_q + 1.1)}"
    P = []
    # conduits from the core's rim down to each card; reads travel outward along them at the end
    for (px, py), a in ((chat, ca), (mcp, ma)):
        sx, sy = _pt(g, g["core"], a)
        d = vcurve_d(sx, sy, px + w / 2, py)
        P.append(f'<path class="f-interfaces-cond" d="{d}"/>' + _pk(d, t_q, .5, _at("query", t_q)))
    P.append(f'<path class="cv f-interfaces-con" d="{con_c}" marker-end="url(#arr)"/>' + _pk(con_c, T_CCONF + .05, .4, ""))
    P.append(f'<path class="cv f-interfaces-con" d="{con_m}" marker-end="url(#arr)"/>' + _pk(con_m, T_MCP[0] + .05, .5, ""))
    P.append(_port(*chat, w, h, "chat", "Chat", ("uploads ≤ 50 MiB", "typed blocks · 3D", "starts imports"),
                   _at("chat", t0, None, f'data-w="{_tv(t0)} {_tv(t1)} {qa}"')))
    P.append(_port(*mcp, w, h, "plug", "MCP server", subs_m,
                   _at("mcp", T_MCP[0], None, f'data-w="{_tv(T_MCP[0])} {_tv(T_MCP[1])} {qa}"')))
    lx, ly, anchor = chips[2]
    P.append(_chip(*chips[0], v, T_CCWAIT, T_CCONF, I_CHAT) + _chip(*chips[1], v, T_CWAIT, T_CONF, I_MCP)
             + f'<text class="lbl" x="{f(lx)}" y="{f(ly)}" text-anchor="{anchor}">unless trusted for writes</text>')
    return "".join(P)


def _wide(lanes, E, t_count, t_q):
    g, v, pre = G["wide"], "wide", "if-w"
    P = [_defs(pre), _keys(v), _hub(g, v, pre, lanes, E), _inline(g, v), _core_text(g, v, t_count)]
    P += [_planet(g, i, v, True) for i in range(len(SRC))]
    P.append(_ports(g, v, t_q))
    H = 840
    P.append(legend(LEGEND, 30, H - 18) + note(g["W"] - 30 - 23 * CW[v], H - 18))
    assert 30 + sum(30 + int(len(t) * 8.1) + 22 for _, t in LEGEND) < g["W"] - 30 - 23 * CW[v]
    return svg(g["W"], H, "".join(P), v, LABEL)


def _narrow(lanes, E, t_count, t_q):
    g, v, pre = G["narrow"], "narrow", "if-n"
    P = [_defs(pre), hdr(12, 24, "SOURCES")]
    for i, (title, det, how, ic, kind, _a) in enumerate(SRC):
        y0 = 40 + 66 * i  # title, detail, then the mapping keyed by its gate glyph
        P.append(f'<circle class="f-interfaces-pl" cx="26" cy="{y0 + 15}" r="13"/>'
                 f'<use class="ic" href="#i-{ic}" x="19" y="{y0 + 8}" width="14" height="14"/>'
                 f'<text class="ttl sm" x="50" y="{y0 + 10}">{escape(title)}</text>'
                 f'<text class="sub" x="50" y="{y0 + 31}">{escape(det)}</text>'
                 + _glyph(50, y0 + 39, 26, 16, kind)
                 + f'<text class="sub f-interfaces-how {kind}" x="86" y="{y0 + 51}">{escape(how)}</text>')
    P += [_hub(g, v, pre, lanes, E), _inline(g, v), _core_text(g, v, t_count)]
    P += [_planet(g, i, v, False) for i in range(len(SRC))]
    P.append(_ports(g, v, t_q))
    ly = 818 + 92 + 48 + 44 + 40
    P.append("".join(legend([it], 12, ly + 26 * k) for k, it in enumerate(LEGEND)) + note(12, ly + 26 * len(LEGEND)))
    return svg(g["W"], ly + 26 * len(LEGEND) + 14, "".join(P), v, LABEL)


JS = """MAFig.register("interfaces", function (root, variant) {
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var timed = q("[data-t]:not([data-w]):not([data-m])"), windows = q("[data-w]"), pks = q("[data-m]");
  var shown = timed.concat(windows, pks), orbit = q(".f-interfaces-orbit");
  gsap.set(orbit, {svgOrigin: orbit[0].getAttribute("data-o")});
  // one pass from t0: every mark shows only after the step that decides it (data-t, checked at build time).
  // Every key in a fromTo start object is repeated in its end object (a loop wrap drops start-only keys).
  function pass(tl, t0) {
    timed.forEach(function (el) { tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: .3}, t0 + +el.getAttribute("data-t")); });
    windows.forEach(function (el) {
      el.getAttribute("data-w").split(" ").forEach(function (s, k) {
        if (k === 0) tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: .15}, t0 + +s);
        else tl.to(el, {opacity: k % 2 ? 0 : 1, duration: .15}, t0 + +s);
      });
    });
    // a record is a short lit stretch of its lane: it moves (start, duration, head %) and fades once it docks
    pks.forEach(function (p) {
      var m = p.getAttribute("data-m").split(" ").map(Number), s = +p.getAttribute("data-sl"), n = m.length;
      var seg = function (h) { return Math.max(0, h - s) + "% " + h + "%"; };
      tl.fromTo(p, {drawSVG: "0% 0%", opacity: 1}, {drawSVG: seg(m[2]), opacity: 1, duration: m[1], ease: "power1.inOut"}, t0 + m[0]);
      for (var j = 3; j < n; j += 3) tl.to(p, {drawSVG: seg(m[j + 2]), duration: m[j + 1], ease: "power1.inOut"}, t0 + m[j]);
      tl.to(p, {opacity: 0, duration: .15}, t0 + m[n - 3] + m[n - 2]);
    });
  }
  var intro = gsap.timeline({defaults: {ease: "power3.out"}});
  intro.from(q(".hdr, .legend"), {opacity: 0, duration: .5}, 0)
    .from(q(".f-interfaces-core"), {opacity: 0, scale: .85, transformOrigin: "50% 50%", duration: .6}, 0)
    .from(q(".f-interfaces-slots circle"), {opacity: 0, duration: .2, stagger: .015}, .2)
    .from(q(".f-interfaces-chk"), {drawSVG: "50% 50%", duration: .6}, .25)
    // dashed shapes fade in: drawSVG would replace their dash pattern
    .from(q(".f-interfaces-rev, .f-interfaces-ring"), {opacity: 0, duration: .5}, .4)
    .from(q(".f-interfaces-gate"), {opacity: 0, duration: .35, stagger: .05}, .5)
    .from(orbit, {opacity: 0, duration: .8}, .4)
    .from(q(".f-interfaces-src"), {opacity: 0, duration: .4, stagger: .07}, .6)
    .from(q(".f-interfaces-lanes, .sub:not([data-t]), .ttl, .f-interfaces-pl, .ic"), {opacity: 0, duration: .5}, .7)
    .from(q(".f-interfaces-port, .f-interfaces-chip, .f-interfaces-cond, .f-interfaces-con, .f-interfaces-cdot, .lbl"), {opacity: 0, y: 8, duration: .5, stagger: .05}, .8)
    .set(shown, {opacity: 0}, 0);
  pass(intro, __T0I__);
  // loop: the orbit drifts (whole dash periods, so the wrap is seamless); hold the finished frame, clear what the pass
  // reveals (timed marks, windows, records), run again. immediateRender off: the frame stays until then.
  var loop = gsap.timeline({repeat: -1, defaults: {immediateRender: false}});
  loop.fromTo(orbit, {rotation: 0}, {rotation: 8, duration: __TL__, ease: "none"}, 0)
    .to(shown, {opacity: 0, duration: .4}, __HOLD__);
  pass(loop, __T0L__);
  loop.set({}, {}, __TL__);
  return {intro: intro, loop: loop};
});"""


def build():
    lw, ln = _lanes(G["wide"]), _lanes(G["narrow"])
    ew, t_count, t_q = _events(lw)
    en, tcn, tqn = _events(ln)
    _check_order(ew, t_count, t_q)
    _check_order(en, tcn, tqn)
    t_count, t_q = max(t_count, tcn), max(t_q, tqn)  # one timeline length for both variants
    pass_ = t_q + 1.2
    t_loop = T0_LOOP + pass_ + .2
    assert T0_INTRO + pass_ <= 10 and t_loop <= 10.4, (pass_, t_loop)
    js = JS
    for k, val in {"__T0I__": T0_INTRO, "__HOLD__": HOLD, "__T0L__": T0_LOOP, "__TL__": t_loop}.items():
        js = js.replace(k, _tv(val))
    assert "__" not in js
    return Figure(wide=_wide(lw, ew, t_count, t_q), narrow=_narrow(ln, en, t_count, t_q), js=js)
