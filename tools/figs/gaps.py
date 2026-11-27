"""Gaps figure, two panels. (a) Gap closure, GAR 2.1: gaps collected by rules are the rows of a checklist grid whose
columns are the papers the judge sees; papers drop in, a language model (the one dark panel) names a paper and quotes
it, a quote mark fills that cell, and the closure-score odometer ticks (C07-C09, C55). (b) Agreement, LCA 5.1: pairs
of values for one property are joined by brackets that stretch along a relative-deviation line into the consensus,
partial and contradiction bands (C10, C11). The SVG is the finished frame; the GSAP intro animates from hidden states
and the loop replays the drop-and-fill and the bracket stretch."""
from html import escape
import math

from figkit import Figure, curve_d, f, hdr, icon, legend, note, svg

CLAIMS = ("C07", "C08", "C09", "C10", "C11", "C55")  # register rows this figure's text and aria-label rest on

T_LOOP = 11.6
A0 = 5.8  # loop: panel b replays first (after a hold on the finished frame), then panel a from A0
# literature gaps (illustrative), verdict and the paper named (1-based); rejected = a closed verdict whose quote has
# none of the gap's own terms, so the gap stays open
GAPS = [("4.5 V cycling data", "closed", 2), ("Li/Ni mixing vs dopant", "closed", 5),
        ("thermal runaway onset", "open", None), ("Co-free compositions", "rejected", 7),
        ("synthesis temperature", "closed", 9)]
N_PAPERS, N_READ = 10, 3  # the PDFs read first, then the search results
QUOTE = ("[9] “", "synthesis", " at 750 °C under O₂”")  # the middle part is the gap term the quote contains
SCORES = ["0", "20", "40", "60"]  # 100 × closed ÷ judged, one step per closed gap
CLOSED = ["0", "1", "2", "3"]
RULES = ["domain checklist", "query gap list", "database coverage"]
STEPS = [("AUGMENT summaries", "≤ 3 sources at once"), ("number + unit", "by pattern matching"),
         ("label: keyword", "120 chars before it"), ("units converted", "→ eV, V and K")]
REEXTRACT = ("language model", "re-extracts conflicts")
# pairs: property, (value, note) for source A and B, relative deviation in % (None: units differ, not compared)
PAIRS = [("overpotential", ("320 mV", "→ 0.32 V"), ("0.322 V", ""), .62),
         ("activation energy", ("82 kJ/mol", "→ 0.85 eV"), ("0.91 eV", ""), 6.6),
         ("Faradaic efficiency", ("92\u202f%", ""), ("71\u202f%", ""), 22.8),
         ("band gap", ("0.9 eV", "PBE"), ("2.1 eV", "HSE06"), 57.1),
         ("band gap", ("2.1 eV", ""), ("590 nm", "nm: no conversion"), None)]
NOTES_N = ["320 mV → 0.32 V", "82 kJ/mol → 0.85 eV", "", "PBE vs HSE06", "nm: no conversion"]  # narrow rows
DEV_MAX = 60.0  # the deviation axis runs 0-60 % on a square-root scale
TICKS = [0, 1, 10, 20, 50]
LABEL = ("Panel a, gap closure: GAR 2.1 collects gaps by rules, without a language model, from the domain's gap "
         "checklist, the database query's gap list and database coverage; record-count gaps are listed separately "
         "and a few gap terms join the paper search. GAR runs one round per run and stops at its run limit, 600\u202fs by default. Up to "
         "ten papers, the PDFs read first and then the search results, drop into the checklist grid, each shown to "
         "the judge as its title and the first 600 characters (by default) of its abstract. In one call a "
         "language model judges every gap: a gap is closed only when the model names a paper and gives a quote "
         "containing one of the gap's own terms, and the quote is not checked against the abstract. The closure "
         "score is 100 × closed ÷ judged, a model-assisted measure of the run's own output, with a word-overlap "
         "fallback. Panel b, agreement: LCA 5.1 pulls numbers with units from each source's summary, labels and "
         "converts them, and compares each pair for one property by relative deviation: up to 1\u202f% is consensus, up "
         "to 10\u202f% (adjustable) partial agreement and above that a contradiction, rated low, medium or high; values "
         "whose units differ are not compared, and, when one is available, a language model re-extracts conflicting "
         "findings. The gaps, values and score are illustrative.")
LEGEND = [("tick", "closed: paper named, quoted"), ("cell", "empty: no paper named"),
          ("xbox", "rejected: no gap term"), ("amber", "contradiction"), ("dash", "optional · fallback")]


LATE = "cv f-gaps-in f-gaps-late"  # connectors into and out of the judge, drawn with the panel
BCONN = "cv f-gaps-in f-gaps-bconn"  # panel b connectors, drawn with panel b


def _flow(d, t, cls="cv f-gaps-in", arrow=True):
    """Connector plus its teal flow overlay (hidden in the static frame), which the loop runs at time t."""
    m = ' marker-end="url(#arr)"' if arrow else ""
    return f'<path class="{cls}" d="{d}"{m}/><path class="f-gaps-flow" d="{d}" data-t="{t}" opacity="0"/>'


def _defs(pre):
    return (f'<defs><linearGradient id="{pre}-pnl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="f-gaps-g0"/>'
            '<stop offset="1" class="f-gaps-g1"/></linearGradient></defs>')


def _chip(x, y, w, h, text):
    return (f'<g class="card f-gaps-rule"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="8"/>'
            f'<circle class="f-gaps-dot" cx="{f(x + 10)}" cy="{f(y + h / 2)}" r="3"/>'
            f'<text class="sub" x="{f(x + 20)}" y="{f(y + h / 2 + 4.5)}">{escape(text)}</text></g>')


def _bin(x, y, w, sub):
    return (f'<g class="card f-gaps-bin"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="52" rx="8"/>'
            f'<text class="tag" x="{f(x + 12)}" y="{f(y + 21)}">COVERAGE GAPS</text>'
            f'<text class="sub" x="{f(x + 12)}" y="{f(y + 40)}">{escape(sub)}</text></g>')


def _paper(cx, y, n, read):
    """A paper glyph (folded corner, title and abstract lines, its number); read papers are outlined in teal."""
    w, h = 26, 34
    x = cx - w / 2
    return (f'<g class="f-gaps-paper{" read" if read else ""}">'
            f'<path class="f-gaps-sheet" d="M{f(x)},{f(y)} h{w - 7} l7,7 V{f(y + h)} H{f(x)} Z"/>'
            f'<path class="f-gaps-pl" d="M{f(x + 4)},{f(y + 8)} h{w - 14} M{f(x + 4)},{f(y + 13)} h{w - 9}"/>'
            f'<text class="f-gaps-pn" x="{f(cx)}" y="{f(y + h - 5)}" text-anchor="middle">{n}</text></g>')


def _check(x, y, state):
    """Checklist box: a teal tick when closed, an amber cross when rejected, empty when open."""
    box = f'<rect class="f-gaps-box" x="{f(x)}" y="{f(y)}" width="18" height="18" rx="4"/>'
    if state == "open":
        return box
    tick = (f'M{f(x + 4.5)},{f(y + 9.5)} l3.5,3.5 l6,-7' if state == "closed" else
            f'M{f(x + 5)},{f(y + 5)} l8,8 M{f(x + 13)},{f(y + 5)} l-8,8')
    a = "" if state == "closed" else " amb"
    # the verdict's tint and mark sit over the neutral box, so they appear and clear with the verdict
    return (box + f'<rect class="f-gaps-boxfill{a}" x="{f(x)}" y="{f(y)}" width="18" height="18" rx="4"/>'
            f'<path class="f-gaps-tick{a}" d="{tick}"/>')


def _grid(gx, y0, cp, cs, rp, box_x, lbl_x, wide):
    """Rows: checkbox, gap label, then one cell per paper; the named paper's cell holds the quote mark."""
    P = [f'<rect class="f-gaps-scan" x="{f(box_x - 6)}" y="{f(y0 - 5 + (0 if wide else -24))}" '
         f'width="{f(gx + (N_PAPERS - 1) * cp + cs + 6 - box_x + 6)}" height="{f(cs + 10 + (0 if wide else 24))}" '
         f'rx="8" opacity="0" data-pitch="{rp}"/>']
    for i, (gap, state, paper) in enumerate(GAPS):
        cy = y0 + i * rp
        ly = cy + cs / 2 + 5 if wide else cy - 10  # narrow: the label sits on its own line above the cells
        P.append(f'<g class="f-gaps-row">{_check(box_x, ly - 14, state)}'
                 f'<text class="sub f-gaps-gap" x="{f(lbl_x)}" y="{f(ly)}">{escape(gap)}</text></g>')
        for k in range(N_PAPERS):
            x = gx + k * cp
            on = paper is not None and k == paper - 1
            P.append(f'<rect class="f-gaps-cell" x="{f(x)}" y="{f(cy)}" width="{cs}" height="{cs}" rx="5"/>')
            if on:  # the verdict overlays the neutral cell: its tint and the quote mark pop and clear together
                qx, qy = x + cs / 2, cy + cs / 2 + 13
                q = (f'<rect class="f-gaps-qfill" x="{f(x)}" y="{f(cy)}" width="{cs}" height="{cs}" rx="5"/>'
                     f'<text class="f-gaps-qm" x="{f(qx)}" y="{f(qy)}" text-anchor="middle">“</text>')
                if state == "closed":
                    P.append(f'<g class="f-gaps-quote" data-row="{i}">{q}</g>')
                else:
                    P.append(f'<g class="f-gaps-quote amb" data-row="{i}">{q}<path class="f-gaps-strike" '
                             f'd="M{f(x + 5)},{f(cy + cs - 5)} L{f(x + cs - 5)},{f(cy + 5)}"/></g>')
    return "".join(P)


def _odo(pre, key, x, y, values, cls, pitch, clip_w, clip_h, anchor="start"):
    """Odometer: the values stacked below the shown one, in a clip window; the loop rolls the stack. The static
    frame shows the last value."""
    n = len(values)
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    cx = x - clip_w if anchor == "end" else x - 2
    t = "".join(f'<text class="{cls}" x="{f(x)}" y="{f(y + (n - 1 - k) * pitch)}"{a}>{v}</text>'
                for k, v in enumerate(values))
    return (f'<clipPath id="{pre}-{key}"><rect x="{f(cx)}" y="{f(y - clip_h + 4)}" width="{f(clip_w + 4)}" '
            f'height="{f(clip_h + 2)}"/></clipPath><g clip-path="url(#{pre}-{key})">'
            f'<g class="f-gaps-odo" data-pitch="{pitch}" data-n="{n}">{t}</g></g>')


def _panel(pre, x, y, w, h, wide):
    """The closure judge, the figure's one dark panel."""
    subs = ["judges closure", "one call, all gaps"]
    P = [f'<g class="f-gaps-judge"><rect class="panel" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="14" '
         f'style="fill:url(#{pre}-pnl)"/>{icon("evaluate", x + 16, y + 17, "ic f-gaps-pic")}'
         f'<text class="f-gaps-lmt" x="{f(x + 42)}" y="{f(y + 32)}">Language model</text>']
    P += [f'<text class="sub f-gaps-on" x="{f(x + 16)}" y="{f(y + 56 + 20 * k)}">{escape(s)}</text>'
          for k, s in enumerate(subs)]
    dy = y + 56 + 20 * len(subs) - 4
    for label, value in (("per gap: closed?", "paper # + quote"), ("quote must contain", "a term of the gap")):
        P.append(f'<g class="f-gaps-dock"><rect x="{f(x + 12)}" y="{f(dy)}" width="{f(w - 24)}" height="46" rx="8"/>'
                 f'<text class="sub f-gaps-on" x="{f(x + 24)}" y="{f(dy + 19)}">{escape(label)}</text>'
                 f'<text class="sub f-gaps-pv" x="{f(x + 24)}" y="{f(dy + 38)}">{escape(value)}</text></g>')
        dy += 52
    return "".join(P) + "</g>"


def _score(pre, x, y, w, h, wide):
    """Closure-score card: the score odometer, its formula, the closed-count odometer and the fallback."""
    nx, ny = x + 16, y + 64
    fx = x + 16 if wide else x + 112
    fy = y + 92 if wide else y + 52
    return (f'<g class="card f-gaps-score"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
            f'<text class="tag" x="{f(x + 16)}" y="{f(y + 24)}">CLOSURE SCORE</text>'
            + _odo(pre, "sc", nx, ny, SCORES, "f-gaps-num", 52, 64, 34)
            + f'<text class="sub" x="{f(fx)}" y="{f(fy)}">100 × closed ÷ judged</text>'
            + _odo(pre, "cl", fx, fy + 20, CLOSED, "sub f-gaps-cnt", 24, 10, 16)
            + f'<text class="sub" x="{f(fx + 14)}" y="{f(fy + 20)}">closed ÷ 5 judged</text>'
            f'<text class="sub" x="{f(fx)}" y="{f(fy + 40)}">fallback: word overlap</text></g>')


def _bubble(x, y, w, h, tail_x):
    """Quote callout with its tail pointing up at the closed cell; the gap term in the quote is highlighted."""
    r = 10
    d = (f"M{f(x + r)},{f(y)} H{f(tail_x - 7)} L{f(tail_x)},{f(y - 9)} L{f(tail_x + 7)},{f(y)} H{f(x + w - r)} "
         f"Q{f(x + w)},{f(y)} {f(x + w)},{f(y + r)} V{f(y + h - r)} Q{f(x + w)},{f(y + h)} {f(x + w - r)},{f(y + h)} "
         f"H{f(x + r)} Q{f(x)},{f(y + h)} {f(x)},{f(y + h - r)} V{f(y + r)} Q{f(x)},{f(y)} {f(x + r)},{f(y)} Z")
    a, term, b = QUOTE
    return (f'<g class="f-gaps-bubble"><path class="f-gaps-bub" d="{d}"/>'
            f'<text class="tag" x="{f(x + 12)}" y="{f(y + h / 2 + 4.5)}">QUOTE</text>'
            f'<text class="f-gaps-qt" x="{f(x + 70)}" y="{f(y + h / 2 + 5)}">{escape(a)}'
            f'<tspan class="f-gaps-hit">{term}</tspan>{escape(b)}</text></g>')


def _step(x, y, w, h, l1, l2, dashed=False, inline=False):
    d = " dashed" if dashed else ""
    if inline:  # narrow: both texts on one line
        t = (f'<text class="sub f-gaps-k" x="{f(x + 12)}" y="{f(y + h / 2 + 4.5)}">{escape(l1)}</text>'
             f'<text class="sub" x="{f(x + w - 12)}" y="{f(y + h / 2 + 4.5)}" text-anchor="end">{escape(l2)}</text>')
    else:
        t = (f'<text class="sub f-gaps-k" x="{f(x + 12)}" y="{f(y + 20)}">{escape(l1)}</text>'
             f'<text class="sub" x="{f(x + 12)}" y="{f(y + 38)}">{escape(l2)}</text>')
    return (f'<g class="card f-gaps-step{d}"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="8"/>'
            f'{t}</g>')


def _dx(x0, length, dev):
    return x0 + length * math.sqrt(dev / DEV_MAX)


def _band_cls(dev):
    return "con" if dev <= 1 else "par" if dev <= 10 else "ctr"


def _bracket(x0, length, y, dev, label_left):
    """A pair's bracket from 0 to its deviation, its end dot and the deviation label."""
    x1 = _dx(x0, length, dev)
    c = _band_cls(dev)
    txt = f"{dev:.1f}\u202f%" if dev < 10 else f"{dev:.0f}\u202f%"
    lx, anc, ly = (x1 - 10, "end", y - 8) if label_left else (x1 + 9, "start", y + 4.5)
    return (f'<path class="f-gaps-brk {c}" d="M{f(x0)},{f(y - 8)} V{f(y)} H{f(x1)} V{f(y - 8)}" '
            f'vector-effect="non-scaling-stroke" data-len="{f(x1 - x0)}"/>'
            f'<circle class="f-gaps-end {c}" cx="{f(x1)}" cy="{f(y)}" r="4.5" data-len="{f(x1 - x0)}"/>'
            f'<text class="sub f-gaps-dev {c}" x="{f(lx)}" y="{f(ly)}" text-anchor="{anc}">{txt}</text>')


def _axis(x0, length, y, sev_y=None):
    """Deviation axis, square-root scale: ticks and labels; severity words under the contradiction band."""
    P = [f'<path class="f-gaps-axis" d="M{f(x0)},{f(y)} H{f(x0 + length)}"/>']
    for t in TICKS:
        x, lab = _dx(x0, length, t), str(t) if t == 0 else f"{t}\u202f%"
        P.append(f'<path class="f-gaps-axis" d="M{f(x)},{f(y)} v6"/>'
                 f'<text class="sub f-gaps-bl" x="{f(x)}" y="{f(y + 22)}" text-anchor="middle">{lab}</text>')
    if sev_y is not None:
        for word, a, b in (("low", 10, 20), ("medium", 20, 50), ("high", 50, DEV_MAX)):
            x = (_dx(x0, length, a) + _dx(x0, length, b)) / 2
            P.append(f'<text class="sub amb f-gaps-bl" x="{f(x)}" y="{f(sev_y)}" text-anchor="middle">{word}</text>')
    return "".join(P)


def _bands(x0, length, y, h):
    P = []
    for c, a, b in (("con", 0, 1), ("par", 1, 10), ("ctr", 10, DEV_MAX)):
        xa, xb = _dx(x0, length, a), _dx(x0, length, b)
        P.append(f'<rect class="f-gaps-band {c}" x="{f(xa)}" y="{f(y)}" width="{f(xb - xa)}" height="{f(h)}"/>')
    return "".join(P)


def _vchip(x, y, w, h, value, note):
    if note:
        t = (f'<text class="f-gaps-val" x="{f(x + 12)}" y="{f(y + 17)}">{escape(value)}</text>'
             f'<text class="sub" x="{f(x + 12)}" y="{f(y + 34)}">{escape(note)}</text>')
    else:
        t = f'<text class="f-gaps-val" x="{f(x + 12)}" y="{f(y + h / 2 + 5)}">{escape(value)}</text>'
    return f'<g class="card f-gaps-vc"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="8"/>{t}</g>'


WIDE = {"W": 1100, "H": 958}


def _wide():
    W, H, pre = WIDE["W"], WIDE["H"], "gaps-w"
    P = [_defs(pre), hdr(30, 34, "a · GAP CLOSURE · GAR 2.1"),
         '<text class="lbl f-gaps-note" x="1070" y="34" text-anchor="end">one round per run · 600\u202fs limit (default)</text>']
    # gaps, by rules
    P.append(hdr(30, 70, "GAPS · BY RULES") + '<text class="lbl f-gaps-note" x="30" y="88">no language model</text>')
    P += [_chip(30, 100 + 38 * k, 160, 30, t) for k, t in enumerate(RULES)]
    gx, cp, cs, y0, rp = 440, 34, 28, 146, 40
    bmid = y0 + (len(GAPS) - 1) * rp / 2 + cs / 2
    P.append(f'<path class="f-gaps-brk0" d="M218,{y0} H212 V{y0 + (len(GAPS) - 1) * rp + cs} H218"/>')
    P += [_flow(curve_d(190, 115 + 38 * k, 210, bmid), A0 + .2 + .1 * k, arrow=k == 1) for k in range(3)]
    P.append(_flow("M60,206 V224", A0 + .5) + _bin(30, 228, 160, "listed separately"))
    P.append(icon("search", 30, 300, "ic f-gaps-sic")
             + '<text class="sub f-gaps-note" x="54" y="312">gap terms join</text>'
             '<text class="sub f-gaps-note" x="54" y="330">the paper search</text>')
    # papers, then the grid
    P.append(hdr(232, 70, "LITERATURE GAPS") + hdr(gx, 70, "≤ 10 PAPERS")
             + f'<text class="lbl f-gaps-note" x="{gx + N_PAPERS * cp - 6}" y="70" text-anchor="end">title + first 600 chars (default)</text>'
             f'<text class="lbl f-gaps-note" x="{gx}" y="90">read first</text>'
             f'<text class="lbl f-gaps-note" x="{gx + N_READ * cp}" y="90">then search results</text>')
    P.append(_grid(gx, y0, cp, cs, rp, 232, 258, True))
    P += [_paper(gx + k * cp + cs / 2, 100, k + 1, k < N_READ) for k in range(N_PAPERS)]
    gr = gx + (N_PAPERS - 1) * cp + cs  # grid right edge
    # the judge, the verdicts back into the grid, and the score
    px, py, pw, ph = 866, 56, 204, 200
    P.append(_flow(curve_d(gr + 4, 117, px - 4, 117), A0 + 1.6, LATE))
    P.append(_flow(curve_d(px - 4, 236, gr + 6, 236), A0 + 2.0, LATE)
             + f'<text class="lbl f-gaps-vlbl" x="{f((gr + px) / 2)}" y="226" text-anchor="middle">verdicts</text>')
    P.append(_panel(pre, px, py, pw, ph, True))
    P.append(_score(pre, px, 290, pw, 140, True))
    tail = gx + (GAPS[4][2] - 1) * cp + cs / 2
    P.append(_bubble(gx, 350, gr - gx, 36, tail))
    P.append(f'<text class="lbl f-gaps-bnote" x="{gx}" y="410">has a gap term · not checked against the abstract</text>')
    # panel b
    P.append('<path class="f-gaps-div" d="M30,440 H1070"/>')
    P.append(hdr(30, 474, "b · AGREEMENT · LCA 5.1")
             + '<text class="f-gaps-fx" x="1070" y="474" text-anchor="end">deviation = |a − b| ÷ max(|a|, |b|)</text>')
    sy, sw, sg = 492, 190, 24
    for k, (l1, l2) in enumerate(STEPS):
        x = 30 + k * (sw + sg)
        P.append(_step(x, sy, sw, 48, l1, l2))
        if k:
            P.append(_flow(f"M{x - sg + 2},{sy + 24} H{x - 2}", 1.0 + .2 * k, BCONN))
    P.append(_step(886, sy, 184, 48, *REEXTRACT, dashed=True))
    x0, L = 540, 510
    ry0, rpb, ch = 604, 52, 40
    bt, bb = ry0 - 6, ry0 + (len(PAIRS) - 1) * rpb + ch + 6
    nc = sum(p[3] is not None for p in PAIRS)  # compared pairs come first; the bands stop above "not compared"
    P.append(_bands(x0, L, bt, ry0 + (nc - 1) * rpb + ch + 6 - bt))
    P.append(f'<path class="cv f-gaps-opt" d="M{x0 + L},{bt + 2} C1060,{bt + 2} 1060,{bt - 6} 1060,{bt - 18} V{sy + 52}" marker-end="url(#arr)"/>')
    for word, sub, a, b in (("consensus", "≤ 1\u202f%", 0, 1), ("partial ≤ 10\u202f%", "adjustable 2–30\u202f%", 1, 10),
                            ("contradiction > 10\u202f%", None, 10, DEV_MAX)):
        cx = (_dx(x0, L, a) + _dx(x0, L, b)) / 2
        P.append(f'<text class="lbl f-gaps-bl" x="{f(cx)}" y="572" text-anchor="middle">{escape(word)}</text>')
        if sub:
            P.append(f'<text class="sub f-gaps-bl" x="{f(cx)}" y="590" text-anchor="middle">{escape(sub)}</text>')
    for a in (20, 50):  # severity steps inside the contradiction band
        P.append(f'<path class="f-gaps-sev" d="M{f(_dx(x0, L, a))},{bt - 18} V{bt}"/>')
    P.append(_axis(x0, L, bb + 8, sev_y=590))
    P.append(hdr(30, 590, "PROPERTY") + hdr(186, 590, "SOURCE A") + hdr(346, 590, "SOURCE B"))
    for i, (prop, a, b, dev) in enumerate(PAIRS):
        y = ry0 + i * rpb
        mid = y + ch / 2
        P.append(f'<g class="f-gaps-prow"><text class="f-gaps-prop" x="30" y="{f(mid + 5)}">{escape(prop)}</text>'
                 + _vchip(180, y, 150, ch, *a) + _vchip(340, y, 150, ch, *b) + '</g>')
        if dev is None:
            P.append(f'<text class="lbl f-gaps-skip" x="{x0 + 10}" y="{f(mid + 5)}">units differ: not compared</text>')
        else:
            P.append(_bracket(x0, L, mid, dev, label_left=dev > 40))
            if b[1] == "HSE06":
                P.append(f'<text class="lbl amb f-gaps-flag" x="{f(_dx(x0, L, 20) - 8)}" y="{f(mid - 8)}" '
                         f'text-anchor="end">different methods: flagged</text>')
    P.append(f'<text class="lbl f-gaps-bl" x="{x0 - 14}" y="{bb + 30}" text-anchor="end">relative deviation, √ scale</text>')
    # four swatches on the first row; the dashed one shares the second row with the note
    assert 30 + sum(30 + int(len(t) * 8.1) + 22 for _, t in LEGEND[:4]) <= 1070
    P.append(legend(LEGEND[:4], 30, H - 38) + legend(LEGEND[4:], 30, H - 12)
             + note(30 + 30 + int(len(LEGEND[4][1]) * 8.1) + 22, H - 12))
    return svg(W, H, "".join(P), "wide", LABEL)


NARROW = {"W": 360}  # the height follows the layout


def _narrow():
    W, pre = NARROW["W"], "gaps-n"
    P = [_defs(pre), hdr(16, 24, "a · GAP CLOSURE · GAR 2.1"),
         '<text class="lbl f-gaps-note" x="16" y="44">one round per run · 600\u202fs limit (default)</text>']
    P.append(hdr(16, 78, "GAPS · BY RULES")
             + '<text class="lbl f-gaps-note" x="344" y="78" text-anchor="end">no language model</text>')
    P.append(_chip(16, 90, 160, 30, RULES[0]) + _chip(184, 90, 160, 30, RULES[1]) + _chip(16, 126, 160, 30, RULES[2]))
    P.append(_flow("M178,141 H192", A0 + .5) + _bin(196, 126, 148, "kept separate"))
    P.append(_flow("M26,158 V310", A0 + .3))
    P.append(icon("search", 40, 186, "ic f-gaps-sic") + '<text class="sub f-gaps-note" x="64" y="199">gap terms join the</text>'
             '<text class="sub f-gaps-note" x="64" y="217">paper search</text>')
    gx, cp, cs, rp = 40, 31, 26, 62
    P.append(hdr(gx, 244, "≤ 10 PAPERS")
             + '<text class="lbl f-gaps-note" x="344" y="244" text-anchor="end">title + 600 chars (default)</text>'
             f'<text class="lbl f-gaps-note" x="{gx}" y="262">read first</text>'
             f'<text class="lbl f-gaps-note" x="{gx + N_READ * cp}" y="262">then search results</text>')
    y0 = 340
    P.append(_grid(gx, y0, cp, cs, rp, 16, 42, False))
    P += [_paper(gx + k * cp + cs / 2, 270, k + 1, k < N_READ) for k in range(N_PAPERS)]
    gb = y0 + (len(GAPS) - 1) * rp + cs  # grid bottom
    tail = gx + (GAPS[4][2] - 1) * cp + cs / 2
    P.append(_bubble(16, gb + 16, 328, 36, tail))
    P.append(f'<text class="lbl f-gaps-bnote" x="344" y="{gb + 72}" text-anchor="end">has a gap term · not checked</text>'
             f'<text class="lbl f-gaps-bnote" x="344" y="{gb + 90}" text-anchor="end">against the abstract</text>')
    py = gb + 116
    # papers and gaps down the right rail into the judge; verdicts up the left rail into the checklist
    P.append(_flow(f"M{gx + N_PAPERS * cp - 1},287 H352 V{py + 30} H348", A0 + 1.6, LATE))
    P.append(_flow(f"M12,{py + 30} H8 V{y0 + 2 * rp - 15} H13", A0 + 2.0, LATE)
             + f'<text class="lbl f-gaps-vlbl" x="24" y="{gb + 108}">verdicts</text>')
    P.append(_panel(pre, 16, py, 328, 200, False))
    sy = py + 220
    P.append(_score(pre, 16, sy, 328, 120, False))
    # panel b
    yb = sy + 150
    P.append(f'<path class="f-gaps-div" d="M16,{yb} H344"/>')
    P.append(hdr(16, yb + 34, "b · AGREEMENT · LCA 5.1")
             + f'<text class="f-gaps-fx" x="16" y="{yb + 58}">deviation = |a − b| ÷ max(|a|, |b|)</text>')
    st = yb + 74
    for k, (l1, l2) in enumerate(STEPS):
        P.append(_step(16, st + 48 * k, 328, 34, l1, l2, inline=True))
        if k:
            P.append(_flow(f"M180,{st + 48 * k - 13} V{st + 48 * k - 2}", 1.0 + .2 * k, BCONN))
    P.append(_step(16, st + 48 * 4 + 8, 328, 34, *REEXTRACT, dashed=True, inline=True))
    x0, L = 24, 316
    ky = st + 48 * 4 + 8 + 34 + 30
    for k, (word, a, b) in enumerate((("consensus ≤ 1\u202f%", 0, 1), ("partial ≤ 10\u202f% · 2–30\u202f%", 1, 10),
                                      ("contradiction > 10\u202f%", 10, DEV_MAX))):
        xa, xb = _dx(x0, L, a), _dx(x0, L, b)
        c = _band_cls(b)
        y = ky + 24 * k
        P.append(f'<text class="lbl f-gaps-bl" x="{f(xa if k else x0)}" y="{f(y)}">{escape(word)}</text>'
                 f'<path class="f-gaps-key {c}" d="M{f(xa)},{f(y + 7)} H{f(xb)}"/>')
    r0 = ky + 3 * 24 + 6
    rpn = 74
    for i, (prop, a, b, dev) in enumerate(PAIRS):
        y = r0 + i * rpn
        vals = f"{a[0]} · {b[0]}"
        nt = NOTES_N[i]
        P.append(f'<g class="f-gaps-prow"><text class="f-gaps-prop" x="16" y="{f(y + 14)}">{escape(prop)}</text>'
                 f'<text class="sub f-gaps-val2" x="344" y="{f(y + 14)}" text-anchor="end">{escape(vals)}</text>'
                 + (f'<text class="sub" x="344" y="{f(y + 35)}" text-anchor="end">{escape(nt)}</text>' if nt else "")
                 + "</g>")
        line = y + 62
        if dev is not None:
            P.append(_bands(x0, L, line - 12, 16))
        if dev is None:
            P.append(f'<text class="lbl f-gaps-skip" x="{x0 + 6}" y="{f(line + 0)}">units differ: not compared</text>')
        else:
            P.append(_bracket(x0, L, line, dev, label_left=dev > 40))
            if a[1] == "PBE":
                P.append(f'<text class="lbl amb f-gaps-flag" x="16" y="{f(y + 35)}">methods differ: flagged</text>')
    ay = r0 + len(PAIRS) * rpn + 2
    P.append(_axis(x0, L, ay, sev_y=ay + 42))
    P.append(f'<text class="lbl f-gaps-bl" x="16" y="{ay + 64}">relative deviation, √ scale</text>')
    H = ay + 64 + 24 + 24 * (len(LEGEND) + 1)
    P.append("".join(legend([it], 16, H - 12 - 24 * (len(LEGEND) - k)) for k, it in enumerate(LEGEND)) + note(16, H - 12))
    return svg(W, H, "".join(P), "narrow", LABEL)


JS = """MAFig.register("gaps", function (root, variant) {
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var one = function (s) { return root.querySelector(s); };
  // layout read from the SVG before any from-state is applied
  var scan = one(".f-gaps-scan"), RP = +scan.getAttribute("data-pitch"), odo = q(".f-gaps-odo"),
    papers = q(".f-gaps-paper"), rows = q(".f-gaps-row"), quotes = q(".f-gaps-quote"), ticks = q(".f-gaps-tick"),
    brks = q(".f-gaps-brk"), ends = q(".f-gaps-end"), devs = q(".f-gaps-dev"), bubble = one(".f-gaps-bubble"),
    fills = q(".f-gaps-boxfill"), bnote = q(".f-gaps-bnote");
  var odoTop = function (el) { return -(el.getAttribute("data-n") - 1) * el.getAttribute("data-pitch"); };
  var odoTopF = function (i, el) { return odoTop(el); };
  var len = function (i, el) { return -el.getAttribute("data-len"); };
  // rows whose verdict closes the gap: the odometers step once for each
  var closedRows = q(".f-gaps-quote:not(.amb)").map(function (el) { return +el.getAttribute("data-row"); });
  gsap.set(brks, {transformOrigin: "0% 50%"});
  var intro = gsap.timeline({defaults: {ease: "power3.out"}});
  intro.from(q(".hdr"), {opacity: 0, duration: .5}, 0)
    .from(q(".f-gaps-rule"), {opacity: 0, x: -12, duration: .35, stagger: .08}, .1)
    .from(q(".f-gaps-in:not(.f-gaps-late):not(.f-gaps-bconn)"), {drawSVG: 0, opacity: 0, duration: .5, stagger: .03}, .35)
    .from(q(".f-gaps-bconn"), {drawSVG: 0, opacity: 0, duration: .3, stagger: .1}, 2.35)
    .from(q(".f-gaps-late"), {drawSVG: 0, opacity: 0, duration: .5, stagger: .2}, 1.9)
    .from(q(".f-gaps-vlbl"), {opacity: 0, duration: .3}, 2.2)
    .from(q(".f-gaps-bin, .f-gaps-note, .f-gaps-sic, .f-gaps-brk0"), {opacity: 0, duration: .4, stagger: .02}, .5)
    .from(rows, {opacity: 0, x: -8, duration: .3, stagger: .06}, .5)
    // the gaps are empty cells, then the papers drop into their columns
    .from(q(".f-gaps-cell"), {scale: 0, transformOrigin: "50% 50%", duration: .25, stagger: .008, ease: "back.out(2)"}, .7)
    // they fade in only once they are near their slot, so they never cross the labels above
    .from(papers, {y: -24, duration: .7, stagger: .07, ease: "bounce.out"}, 1.1)
    .from(papers, {opacity: 0, duration: .15, stagger: .07, ease: "power1.in"}, 1.32)
    .from(q(".f-gaps-judge"), {opacity: 0, scale: .96, transformOrigin: "50% 50%", duration: .5}, 1.6)
    .from(q(".f-gaps-dock"), {opacity: 0, x: -10, duration: .3, stagger: .1}, 1.8)
    .from(q(".f-gaps-score"), {opacity: 0, y: 10, duration: .4}, 2.0)
    .fromTo(odo, {y: odoTopF}, {y: odoTopF, duration: .01}, 0);
  // verdicts row by row: the quote mark fills the named cell, the box ticks, the odometers step
  rows.forEach(function (r, i) {
    var t = 2.4 + i * .3, qm = root.querySelector('.f-gaps-quote[data-row="' + i + '"]'), tk = r.querySelector(".f-gaps-tick"),
      bf = r.querySelector(".f-gaps-boxfill");
    if (qm) intro.from(qm, {scale: 0, opacity: 0, transformOrigin: "50% 50%", duration: .4, ease: "back.out(3)"}, t);
    if (bf) intro.from(bf, {opacity: 0, duration: .2}, t + .1);
    if (tk) intro.from(tk, {drawSVG: 0, duration: .3, ease: "none"}, t + .15);
    var k = closedRows.indexOf(i);
    if (k >= 0) odo.forEach(function (o) {
      intro.to(o, {y: odoTop(o) + (k + 1) * o.getAttribute("data-pitch"), duration: .35, ease: "power2.out"}, t + .1);
    });
  });
  intro.from(bubble, {opacity: 0, scale: .92, transformOrigin: "50% 0%", duration: .45, ease: "back.out(2)"}, 4.0)
    .from(bnote, {opacity: 0, duration: .3}, 4.2)
    .from(q(".f-gaps-step"), {opacity: 0, y: 8, duration: .35, stagger: .1}, 2.2)
    .from(q(".f-gaps-band, .f-gaps-key, .f-gaps-bl, .f-gaps-sev, .f-gaps-axis"), {opacity: 0, duration: .5, stagger: .01}, 2.6)
    .from(q(".f-gaps-prow"), {opacity: 0, x: -10, duration: .35, stagger: .08}, 2.7)
    // the brackets stretch out to each pair's deviation
    .from(brks, {scaleX: 0, duration: 1.1, stagger: .18, ease: "elastic.out(1, .55)"}, 3.1)
    .from(ends, {x: len, duration: 1.1, stagger: .18, ease: "elastic.out(1, .55)"}, 3.1)
    .from(ends, {opacity: 0, duration: .15, stagger: .18}, 3.1)
    .from(devs, {opacity: 0, duration: .3, stagger: .18}, 3.6)
    .from(q(".f-gaps-skip, .f-gaps-flag, .f-gaps-opt"), {opacity: 0, duration: .4}, 4.0)
    .from(q(".legend"), {opacity: 0, duration: .4}, 4.3);
  // loop: after a hold on the finished frame the brackets retract and stretch again pair by pair; then the verdicts
  // clear, the papers drop in again and a scan steps down the rows refilling the named cells while the odometers
  // tick. Every key in a fromTo start object is repeated in its end object (a loop wrap drops start-only keys).
  // immediateRender off: the finished frame stays.
  var loop = gsap.timeline({repeat: -1, defaults: {immediateRender: false}});
  loop.to(quotes, {opacity: 0, scale: 0, transformOrigin: "50% 50%", duration: .3}, __A0__)
    .to(ticks, {drawSVG: "0%", duration: .3}, __A0__)
    .to(fills, {opacity: 0, duration: .3}, __A0__)
    .to(bubble, {opacity: 0, duration: .3}, __A0__)
    .to(bnote, {opacity: 0, duration: .3}, __A0__);
  odo.forEach(function (o) { loop.to(o, {y: odoTop(o), duration: .6, ease: "power2.inOut"}, __A0__ + .1); });
  loop.to(papers, {y: -6, opacity: 0, duration: .25, stagger: .03, ease: "power2.in"}, __A0__ + .4)
    .fromTo(papers, {y: -24}, {y: 0, duration: .7, stagger: .06, ease: "bounce.out"}, __A0__ + .9)
    .fromTo(papers, {opacity: 0}, {opacity: 1, duration: .15, stagger: .06, ease: "power1.in"}, __A0__ + 1.12)
    .fromTo(scan, {y: 0, opacity: 0}, {y: 0, opacity: 1, duration: .2}, __A0__ + 2.1);
  rows.forEach(function (r, i) {
    var t = __A0__ + 2.3 + i * .5, qm = root.querySelector('.f-gaps-quote[data-row="' + i + '"]'), tk = r.querySelector(".f-gaps-tick"),
      bf = r.querySelector(".f-gaps-boxfill");
    if (bf) loop.fromTo(bf, {opacity: 0}, {opacity: 1, duration: .2}, t + .1);
    if (i) loop.to(scan, {y: i * RP, duration: .25, ease: "power2.inOut"}, t - .3);
    if (qm) loop.fromTo(qm, {scale: 0, opacity: 0}, {scale: 1, opacity: 1, duration: .4, ease: "back.out(3)"}, t);
    if (tk) loop.fromTo(tk, {drawSVG: "0%"}, {drawSVG: "100%", duration: .3, ease: "none"}, t + .15);
    var k = closedRows.indexOf(i);
    if (k >= 0) odo.forEach(function (o) {
      loop.to(o, {y: odoTop(o) + (k + 1) * o.getAttribute("data-pitch"), duration: .35, ease: "power2.out"}, t + .1);
    });
  });
  loop.to(scan, {opacity: 0, duration: .3}, __A0__ + 4.7)
    .fromTo(bubble, {opacity: 0, scale: .92}, {opacity: 1, scale: 1, transformOrigin: "50% 0%", duration: .45, ease: "back.out(2)"}, __A0__ + 4.7)
    .fromTo(bnote, {opacity: 0}, {opacity: 1, duration: .3}, __A0__ + 4.9);
  q(".f-gaps-flow").forEach(function (el) {
    var t = +el.getAttribute("data-t");
    loop.fromTo(el, {drawSVG: "0% 14%", opacity: 1}, {drawSVG: "86% 100%", opacity: 1, duration: .6, ease: "power1.in"}, t)
      .to(el, {opacity: 0, duration: .15}, t + .6);
  });
  loop.to(brks, {scaleX: 0, duration: .35, stagger: .05, ease: "power2.in"}, 1.5)
    .to(ends, {x: len, duration: .35, stagger: .05, ease: "power2.in"}, 1.5)
    .to(devs, {opacity: 0, duration: .2}, 1.5);
  brks.forEach(function (b, i) {
    var t = 2.2 + i * .6;
    loop.to(b, {scaleX: 1, duration: 1.1, ease: "elastic.out(1, .55)"}, t)
      .to(ends[i], {x: 0, duration: 1.1, ease: "elastic.out(1, .55)"}, t)
      .to(devs[i], {opacity: 1, duration: .3}, t + .5);
  });
  loop.fromTo(q(".f-gaps-skip"), {opacity: .3}, {opacity: 1, duration: .5}, 4.8)
    .set({}, {}, __TL__);
  return {intro: intro, loop: loop};
});""".replace("__TL__", str(T_LOOP)).replace("__A0__", str(A0))

# panel b replays before A0, panel a ends inside the loop period (bubble A0 + 4.7 + .45)
assert 2.2 + (len([p for p in PAIRS if p[3] is not None]) - 1) * .6 + 1.1 <= A0 and A0 + 4.9 + .3 <= T_LOOP


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
