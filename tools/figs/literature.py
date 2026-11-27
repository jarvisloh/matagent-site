"""Literature figure: a reading desk. LR finds papers; a scan beam sweeps the PDF's page stack; BM25 bars rank the
page-text chunks (top k, at most two per page); a lens reads a chart on a page image; a multi-hop path lights across a
knowledge graph; the evidence docks in the language model (the one dark panel), which writes a cited answer
(claims C01-C03, C47, C49, C53). The SVG is the finished frame; the GSAP intro animates from hidden states and the
loop replays the reading: beam, bars, lens, graph path, answer."""
from html import escape

from figkit import Figure, curve_d, f, hdr, icon, legend, note, svg

T_LOOP = 10.4
LENS_S = 1.8  # lens magnification
# loop times (s) of each evidence flow; each flow overlay carries its time as data-t
FT = {"merge": 0, "text": .3, "images": 1.0, "thumbs": 1.6, "chunks": 1.9, "chart": 4.4, "reading": 4.9,
      "graph": 7.2, "answer": 8.1}
QUESTION = {"wide": ("Which dopants", "stabilise Ni-rich", "layered oxides?"),
            "narrow": ("Which dopants stabilise", "Ni-rich layered oxides?")}
SOURCES = [("Semantic Scholar", False), ("Google Scholar", False), ("arXiv · fallback", True)]
# BM25 rows, best first: score (illustrative), page, state (kept; cap = skipped, a third chunk from one page; out = below top k)
ROWS = [(7.9, 4, "kept"), (6.4, 6, "kept"), (5.8, 4, "kept"), (5.1, 4, "cap"), (4.3, 2, "kept"), (2.2, 9, "out")]
KEPT_PAGES = "[p. 4] [p. 6] [p. 2]"
# multi-hop path through illustrative entities, and the relation on each hop
HOPS = ["Ni-rich NMC", "Li/Ni mixing", "Mg doping", "cycle stability"]
RELS = ["shows", "suppressed by", "improves"]
# answer lines: (text, citation, text after it)
ANSWER = {"wide": [("Mg doping suppresses", "", ""), ("Li/Ni mixing ", "[p. 4]", ";"), ("doped cells retain", "", ""),
                   ("more capacity ", "[p. 6]", "")],
          "narrow": [("Mg doping suppresses Li/Ni", "", ""), ("mixing ", "[p. 4]", "; doped cells"),
                     ("retain more capacity ", "[p. 6]", "")]}
READING = ["[p. 6] Mg-doped cells", "retain more capacity"]
LABEL = ("Reading the literature: LR 1.1 turns a question into up to five queries to Semantic Scholar and Google "
         "Scholar, with arXiv as a fallback, merges and ranks the results lexically and downloads the top papers. "
         "Each PDF's page text is split into overlapping chunks of about 1,200 characters and ranked by BM25; the top "
         "k are kept, at most two per page. By default the page images are read too: ColSmol-500M ranks them and a "
         "vision-language model reads the top pages, charts included. With a knowledge-graph source, a graph neural "
         "network follows a multi-hop path across the graph. A language model writes the answer from this evidence, "
         "citing pages as [p. N]. Scores and the example are illustrative.")
LEGEND = [("flow", "evidence to the answer"), ("dash", "optional · fallback"), ("amber", "skipped: over 2 per page")]
LATE = ("chunks", "reading", "graph", "answer")  # connectors into the panel and the answer
EVIDENCE = ("chunks", "reading", "answer")  # solid teal in the static frame (legend: evidence to the answer)


def _flow(d, key, dashed=False, arrow=True):
    """Connector plus its teal flow overlay (hidden in the static frame), which the loop runs at FT[key]."""
    late = " f-literature-late" if key in LATE else ""  # drawn with the panel in the intro
    ev = " f-literature-ev" if key in EVIDENCE else ""
    cls = "cv f-literature-in" + late + ev + (" f-literature-opt" if dashed else "")
    m = ' marker-end="url(#arr)"' if arrow else ""
    return f'<path class="{cls}" d="{d}"{m}/><path class="f-literature-flow" d="{d}" data-t="{FT[key]}" opacity="0"/>'


def _vd(x1, y1, x2, y2):
    """Vertical-tangent cubic from (x1, y1) to (x2, y2)."""
    dy = max(abs(y2 - y1) * .5, 12)
    return f"M{f(x1)},{f(y1)} C{f(x1)},{f(y1 + dy)} {f(x2)},{f(y2 - dy)} {f(x2)},{f(y2)}"


def _defs(pre):
    return (f'<defs><linearGradient id="{pre}-beam" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" class="f-literature-b0" stop-opacity="0"/><stop offset=".5" class="f-literature-b0" stop-opacity=".32"/>'
            '<stop offset="1" class="f-literature-b0" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="{pre}-pnl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="f-literature-g0"/>'
            '<stop offset="1" class="f-literature-g1"/></linearGradient></defs>')


def _question(x, y, w, h, variant):
    q = "".join(f'<text class="f-literature-qt" x="{f(x + 14)}" y="{f(y + 52 + 20 * k)}">{escape(s)}</text>'
                for k, s in enumerate(QUESTION[variant]))
    return (f'<g class="card f-literature-q"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="12"/>'
            f'{icon("chat", x + 14, y + 12)}<text class="tag" x="{f(x + 40)}" y="{f(y + 25)}">ILLUSTRATIVE</text>{q}</g>')


def _chip(x, y, w, h, text, dashed):
    d = " dashed" if dashed else ""
    return (f'<g class="card f-literature-src{d}"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="8"/>'
            f'<circle class="f-literature-srcdot" cx="{f(x + 13)}" cy="{f(y + h / 2)}" r="3"/>'
            f'<text class="sub" x="{f(x + 24)}" y="{f(y + h / 2 + 4.5)}">{escape(text)}</text></g>')


def _lines(x, y, w, n, gap=9, hot=()):
    out = []
    for k in range(n):
        ln = w * (.62 if k % 4 == 3 else .92 - .06 * (k % 3))
        out.append(f'<path class="f-literature-pl{" on" if k in hot else ""}" d="M{f(x)},{f(y + k * gap)} h{f(ln)}"/>')
    return "".join(out)


def _chart(x, y, w, h, marks=True):
    """Capacity retention vs cycle: doped (teal) holds, undoped (muted) fades. Axes, grid and curves, no text."""
    def pts(drop):
        return [(x + w * t, y + h * (.12 + drop * t ** 1.6)) for t in [i / 10 for i in range(11)]]

    def d(p):
        return "M" + " L".join(f"{f(a)},{f(b)}" for a, b in p)
    doped, undoped = pts(.18), pts(.72)
    out = "".join(f'<path class="f-literature-grid" d="M{f(x)},{f(y + h * g)} h{f(w)}"/>' for g in (.25, .5, .75))
    out += (f'<path class="f-literature-axis" d="M{f(x)},{f(y)} V{f(y + h)} H{f(x + w)}"/>'
            f'<path class="f-literature-curve f-literature-c2" d="{d(undoped)}"/><path class="f-literature-curve" d="{d(doped)}"/>')
    if marks:
        out += "".join(f'<circle class="f-literature-mk" cx="{f(a)}" cy="{f(b)}" r="2.2"/>' for a, b in doped[2::2])
        out += "".join(f'<circle class="f-literature-mk2" cx="{f(a)}" cy="{f(b)}" r="2.2"/>' for a, b in undoped[2::2])
    return out


def _stack(pre, x, y, w, h):
    """Fanned page stack (back pages rotate about the bottom-left corner) with the scan beam on the front page."""
    P = []
    for a in (7, 3.5):
        P.append(f'<g transform="rotate({a} {f(x)} {f(y + h)})"><g class="f-literature-page" data-a="{a}" '
                 f'data-o="{f(x)} {f(y + h)}"><rect class="f-literature-sheet" x="{f(x)}" y="{f(y)}" width="{f(w)}" '
                 f'height="{f(h)}" rx="4"/></g></g>')
    fy = y + h * .6  # the page's figure
    P.append(f'<g class="f-literature-front"><rect class="f-literature-sheet" x="{f(x)}" y="{f(y)}" width="{f(w)}" '
             f'height="{f(h)}" rx="4"/><path class="f-literature-pl f-literature-title" d="M{f(x + 12)},{f(y + 16)} h{f(w * .55)}"/>'
             + _lines(x + 12, y + 30, w - 24, 6, 9, hot=(2, 3))
             + f'<rect class="f-literature-fig" x="{f(x + 12)}" y="{f(fy)}" width="{f(w - 24)}" height="{f(h * .26)}" rx="2"/>'
             + _chart(x + 20, fy + 7, w - 40, h * .26 - 14, marks=False)
             + _lines(x + 12, y + h - 14, w - 24, 1) + '</g>')
    by = y + h * .36
    P.append(f'<clipPath id="{pre}-pg"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="4"/></clipPath>'
             f'<g clip-path="url(#{pre}-pg)" class="f-literature-scan" data-range="{f(by - y + 24)} {f(y + h - by)}">'
             f'<rect class="f-literature-beam" x="{f(x - 2)}" y="{f(by)}" width="{f(w + 4)}" height="24" fill="url(#{pre}-beam)"/>'
             f'<path class="f-literature-beamline" d="M{f(x)},{f(by + 12)} h{f(w)}"/></g>')
    return "".join(P)


def _rows(x, y, w, pitch, rh):
    """BM25 rows: two overlapping chunk glyphs, page tag, score bar, score. Returns markup and the cut line's y."""
    P, bx, val_w = [], x + 102, 34
    bmax = w - (bx - x) - val_w - 8
    for i, (score, page, state) in enumerate(ROWS):
        ry = y + i * pitch
        cls = {"kept": " on", "cap": " amb", "out": ""}[state]
        P.append(f'<g class="f-literature-row">'
                 f'<rect class="f-literature-chunk f-literature-ov" x="{f(x + 6)}" y="{f(ry + 4)}" width="40" height="{f(rh - 4)}" rx="4"/>'
                 f'<rect class="f-literature-chunk{cls}" x="{f(x)}" y="{f(ry)}" width="40" height="{f(rh - 4)}" rx="4"/>'
                 + _lines(x + 8, ry + rh / 2 - 5, 24, 2, 6)
                 + f'<text class="sub" x="{f(x + 56)}" y="{f(ry + rh / 2 + 4)}">p. {page}</text>'
                 f'<rect class="f-literature-bar{cls}" x="{f(bx)}" y="{f(ry + rh / 2 - 5)}" width="{f(bmax * score / ROWS[0][0])}" height="10" rx="3"/>'
                 f'<text class="sub f-literature-val{cls}" x="{f(x + w)}" y="{f(ry + rh / 2 + 4)}" text-anchor="end">{score}</text></g>')
    last_kept = max(i for i, r in enumerate(ROWS) if r[2] != "out")
    cy = y + last_kept * pitch + rh + (pitch - rh) / 2
    P.append(f'<path class="f-literature-cut" d="M{f(x)},{f(cy)} H{f(x + w)}"/>')
    return "".join(P), cy


def _thumbs(x, y, n, tw, th, gap):
    """Page images ranked by ColSmol-500M, lowest rank on the left, so the top page (teal, the one read below) sits
    next to the chart it leads to."""
    P = []
    for k in range(n):
        tx, rank = x + k * (tw + gap), n - k
        top = (f'<rect class="f-literature-fig" x="{f(tx + 5)}" y="{f(y + 6)}" width="{tw - 10}" height="{f(th * .34)}" rx="1"/>'
               if rank == 1 else _lines(tx + 5, y + 8, tw - 10, 2, 6))
        P.append(f'<g class="f-literature-thumb{" on" if rank == 1 else ""}"><rect x="{f(tx)}" y="{f(y)}" width="{tw}" height="{th}" rx="3"/>'
                 f'{top}{_lines(tx + 5, y + th * .55, tw - 18, 2, 6)}'
                 f'<text class="f-literature-rank" x="{f(tx + tw - 4)}" y="{f(y + th - 4)}" text-anchor="end">{rank}</text></g>')
    return "".join(P)


def _chart_page(pre, x, y, w, h, lens):
    """Page image with a chart, and the lens: lens = (cx, cy, r, travel). The lens's clip and magnified copy move with it."""
    ax, ay, aw, ah = x + 22, y + 34, w - 40, h - 62
    P = [f'<g class="f-literature-cpage"><rect class="f-literature-sheet" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="4"/>'
         f'<text class="tag" x="{f(x + 12)}" y="{f(y + 22)}">RETENTION</text>'
         f'<text class="tag" x="{f(x + w - 12)}" y="{f(y + h - 10)}" text-anchor="end">CYCLE</text>'
         + _chart(ax, ay, aw, ah) + '</g>']
    lx, ly, r, travel = lens
    m = f"matrix({LENS_S} 0 0 {LENS_S} {f(lx * (1 - LENS_S))} {f(ly * (1 - LENS_S))})"
    P.append(f'<clipPath id="{pre}-lens"><circle cx="{f(lx)}" cy="{f(ly)}" r="{r - 1}"/></clipPath>'
             f'<g class="f-literature-lens" data-travel="{travel}" data-s="{LENS_S}">'
             f'<circle class="f-literature-lensbg" cx="{f(lx)}" cy="{f(ly)}" r="{r}"/>'
             f'<g clip-path="url(#{pre}-lens)"><g class="f-literature-mag"><g transform="{m}">{_chart(ax, ay, aw, ah)}</g></g></g>'
             f'<circle class="f-literature-ring" cx="{f(lx)}" cy="{f(ly)}" r="{r}"/>'
             f'<path class="f-literature-handle" d="M{f(lx + r * .72)},{f(ly + r * .72)} l{f(r * .42)},{f(r * .42)}"/></g>')
    return "".join(P)


def _reading(x, y, w, h, sm=""):
    t = "".join(f'<text class="sub" x="{f(x + 14)}" y="{f(y + 48 + 20 * k)}">{s}</text>'
                for k, s in enumerate(("reads the top pages", "charts and images")))
    t += "".join(f'<text class="sub f-literature-rd" x="{f(x + 14)}" y="{f(y + 104 + 20 * k)}">{escape(s)}</text>'
                 for k, s in enumerate(READING))
    return (f'<g class="card f-literature-read"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
            f'<text class="ttl{sm}" x="{f(x + 14)}" y="{f(y + 26)}">Vision-language model</text>'
            f'<path class="f-literature-rdbar" d="M{f(x + 14)},{f(y + 82)} h{f(w - 28)}"/>{t}</g>')


def _graph(pts, bg, edges, lbl_pos, rel_pos):
    """Knowledge graph: background nodes and edges, then the lit multi-hop path, its numbered hop badges (at the edge
    midpoints) and the relation of each hop."""
    allp = pts + bg
    P = [f'<path class="f-literature-ge" d="M{f(allp[a][0])},{f(allp[a][1])} L{f(allp[b][0])},{f(allp[b][1])}"/>' for a, b in edges]
    P += [f'<path class="f-literature-hop" d="M{f(x1)},{f(y1)} L{f(x2)},{f(y2)}"/>' for (x1, y1), (x2, y2) in zip(pts, pts[1:])]
    P += [f'<circle class="f-literature-gn" cx="{f(x)}" cy="{f(y)}" r="6"/>' for x, y in bg]
    P += [f'<g class="f-literature-hopg"><circle class="f-literature-halo" cx="{f(x)}" cy="{f(y)}" r="15"/>'
          f'<circle class="f-literature-hopnode" cx="{f(x)}" cy="{f(y)}" r="9"/></g>' for x, y in pts]
    P += [f'<text class="sub f-literature-ent" x="{f(tx)}" y="{f(ty)}" text-anchor="{anc}">{escape(HOPS[i])}</text>'
          for i, (tx, ty, anc) in enumerate(lbl_pos)]
    P += [f'<text class="lbl f-literature-rel" x="{f(tx)}" y="{f(ty)}" text-anchor="{anc}">{escape(RELS[i])}</text>'
          for i, (tx, ty, anc) in enumerate(rel_pos)]
    for i, ((x1, y1), (x2, y2)) in enumerate(zip(pts, pts[1:])):
        bx, by = (x1 + x2) / 2, (y1 + y2) / 2
        P.append(f'<g class="f-literature-badge"><circle cx="{f(bx)}" cy="{f(by)}" r="9"/>'
                 f'<text x="{f(bx)}" y="{f(by + 4.5)}" text-anchor="middle">{i + 1}</text></g>')
    P.append(f'<circle class="f-literature-walker" cx="{f(pts[0][0])}" cy="{f(pts[0][1])}" r="5" opacity="0"/>')
    return "".join(P)


def _panel(pre, x, y, w, h, docks, ty):
    """The language model, the figure's one dark panel; docks = [(y, label, value, dashed)]."""
    P = [f'<g class="f-literature-lm"><rect class="panel" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="14" '
         f'style="fill:url(#{pre}-pnl)"/>{icon("augment", x + 16, ty - 14, "ic f-literature-pic")}'
         f'<text class="f-literature-lmt" x="{f(x + 42)}" y="{f(ty)}">Language model</text>'
         f'<text class="sub f-literature-on" x="{f(x + 16)}" y="{f(ty + 24)}">answers, citing pages</text>']
    for dy, label, value, dashed in docks:
        P.append(f'<g class="f-literature-dock{" f-literature-dockopt" if dashed else ""}">'
                 f'<rect x="{f(x + 12)}" y="{f(dy)}" width="{f(w - 24)}" height="48" rx="8"/>'
                 f'<text class="sub f-literature-on" x="{f(x + 24)}" y="{f(dy + 20)}">{escape(label)}</text>'
                 f'<text class="sub f-literature-pv" x="{f(x + 24)}" y="{f(dy + 39)}">{escape(value)}</text></g>')
    return "".join(P) + "</g>"


def _answer(pre, x, y, w, h, variant, tail_x, tail_up):
    """Speech bubble with the cited answer; its text sits in a clip rect the loop widens, so the answer writes in."""
    t = "".join(f'<text class="f-literature-at" x="{f(x + 16)}" y="{f(y + 56 + 21 * k)}">{escape(s)}'
                + (f'<tspan class="f-literature-cite">{c}</tspan>' if c else "") + f'{escape(after)}</text>'
                for k, (s, c, after) in enumerate(ANSWER[variant]))
    r = 14
    if tail_up:
        top = f"H{f(tail_x - 9)} L{f(tail_x)},{f(y - 12)} L{f(tail_x + 9)},{f(y)} "
        bot = ""
    else:
        top = ""
        bot = f"H{f(tail_x + 9)} L{f(tail_x)},{f(y + h + 12)} L{f(tail_x - 9)},{f(y + h)} "
    d = (f"M{f(x + r)},{f(y)} {top}H{f(x + w - r)} Q{f(x + w)},{f(y)} {f(x + w)},{f(y + r)} V{f(y + h - r)} "
         f"Q{f(x + w)},{f(y + h)} {f(x + w - r)},{f(y + h)} {bot}H{f(x + r)} Q{f(x)},{f(y + h)} {f(x)},{f(y + h - r)} "
         f"V{f(y + r)} Q{f(x)},{f(y)} {f(x + r)},{f(y)} Z")
    return (f'<g class="f-literature-answer"><path class="f-literature-bub" d="{d}"/>'
            f'{icon("chat", x + 16, y + 13)}<text class="tag" x="{f(x + 42)}" y="{f(y + 26)}">ILLUSTRATIVE</text>'
            f'<clipPath id="{pre}-ans"><rect class="f-literature-wipe" x="{f(x)}" y="{f(y + 34)}" width="{f(w)}" height="{f(h - 34)}"/></clipPath>'
            f'<g clip-path="url(#{pre}-ans)">{t}</g></g>')


WIDE = {"W": 1100, "H": 776}


def _wide():
    W, H, pre = WIDE["W"], WIDE["H"], "literature-w"
    P = [_defs(pre), hdr(30, 40, "FINDS PAPERS"), hdr(240, 40, "PDF PAGES"), hdr(450, 40, "BM25 · TEXT CHUNKS"),
         hdr(862, 40, "ANSWER")]
    # search: question, queries, sources, merge into the downloaded PDFs
    P.append(_question(30, 56, 180, 112, "wide"))
    P.append('<path class="cv f-literature-q2" d="M44,168 V196" marker-end="url(#arr)"/>'
             '<text class="lbl f-literature-note" x="54" y="187">up to 5 queries</text>')
    P += [_chip(30, 200 + 36 * k, 180, 30, t, dashed) for k, (t, dashed) in enumerate(SOURCES)]
    P.append('<text class="sub f-literature-note" x="30" y="326">merged · de-duplicated</text>'
             '<text class="sub f-literature-note" x="30" y="346">lexical rank · top 5</text>')
    P += [f'<path class="cv f-literature-merge" d="{curve_d(210, 215 + 36 * k, 246, 200)}"' + (' marker-end="url(#arr)"/>' if k == 1 else '/>')
          for k in range(3)]
    P.append(f'<path class="f-literature-flow" d="{curve_d(210, 251, 246, 200)}" data-t="{FT["merge"]}" opacity="0"/>')
    sx, sy, sw, sh = 252, 74, 128, 180
    P.append(_stack(pre, sx, sy, sw, sh))
    # text chunks ranked by BM25
    rx, ry0, rw, pitch = 450, 62, 310, 36
    rows, cut_y = _rows(rx, ry0, rw, pitch, 30)
    P.append(_flow("M402,150 H444", "text") + rows)
    ny = ry0 + 6 * pitch + 16
    P.append(f'<text class="sub f-literature-note" x="{rx}" y="{ny}">overlapping chunks</text>'
             f'<text class="sub f-literature-note" x="{rx + rw}" y="{ny}" text-anchor="end">~1,200 chars each</text>'
             f'<text class="sub f-literature-note" x="{rx}" y="{ny + 20}">top k · ≤ 2 per page</text>'
             f'<text class="lbl f-literature-note" x="{rx - 6}" y="{f(cut_y + 4)}" text-anchor="end">top k</text>')
    # page images: ranked, the top page read through the lens
    P.append(hdr(30, 384, "PAGE IMAGES"))
    P.append(_flow(_vd(316, sy + sh + 8, 147, 396), "images"))  # into the middle of the ranked strip
    P.append(_thumbs(56, 402, 5, 30, 42, 8))
    P.append('<text class="sub f-literature-note" x="30" y="470">ColSmol-500M ranks</text>'
             '<text class="sub f-literature-note" x="30" y="490">the page images</text>')
    P.append(_flow(curve_d(242, 423, 262, 448), "thumbs"))  # from the top-ranked page
    cx_, cy_, cw, ch = 266, 380, 214, 150
    P.append(_chart_page(pre, cx_, cy_, cw, ch, (cx_ + cw - 56, cy_ + 80, 34, 96)))
    P.append(_flow(curve_d(cx_ + cw + 4, 448, 520, 448), "chart"))
    P.append(_reading(524, 380, 236, 150))
    # knowledge graph
    P.append(hdr(30, 578, "KNOWLEDGE GRAPH · GNN"))
    P.append('<text class="sub f-literature-note" x="30" y="600">graph neural network</text>')
    pts = [(96, 668), (284, 640), (470, 690), (650, 630)]
    bg = [(52, 628), (156, 610), (196, 712), (352, 708), (386, 612), (560, 616), (566, 722), (730, 706), (744, 604)]
    edges = [(0, 4), (0, 5), (0, 6), (1, 5), (1, 8), (2, 7), (2, 9), (2, 10), (3, 9), (3, 11), (3, 12), (5, 8),
             (6, 7), (10, 11)]
    P.append(_graph(pts, bg, edges,
                    lbl_pos=[(96, 700, "middle"), (284, 618, "middle"), (470, 722, "middle"), (650, 668, "middle")],
                    rel_pos=[(190, 636, "middle"), (390, 652, "start"), (530, 646, "middle")]))
    # the language model and its docks
    px, py, pw, ph = 862, 236, 208, 420
    docks = [(312, "text chunks", KEPT_PAGES, False), (426, "page readings", "[p. 6]", False),
             (572, "graph path", "3 hops", True)]
    # a bracket gathers the rows above the cut (the top k); the evidence leaves from its middle
    bt, bb = ry0 + 2, ry0 + 4 * pitch + 28
    P.append(f'<path class="f-literature-brk" d="M{rx + rw + 4},{bt} h5 V{bb} h-5"/>')
    P.append(_flow(curve_d(rx + rw + 9, (bt + bb) / 2, px - 4, 336), "chunks"))
    P.append(_flow(curve_d(764, 448, px - 4, 450), "reading"))
    P.append(_flow(curve_d(668, 630, px - 4, 596), "graph", dashed=True))
    P.append('<text class="lbl f-literature-optlbl" x="852" y="660" text-anchor="end">with a graph source</text>')
    P.append(_panel(pre, px, py, pw, ph, docks, 268))
    # the answer
    P.append(_flow(f"M966,{py} V{py - 22}", "answer"))
    P.append(_answer(pre, 862, 56, 208, 142, "wide", 966, tail_up=False))
    P.append(legend(LEGEND, 30, H - 18) + note(740, H - 18))
    return svg(W, H, "".join(P), "wide", LABEL)


NARROW = {"W": 360}  # the height follows the layout


def _narrow():
    W, pre = NARROW["W"], "literature-n"
    X = 36  # lane content starts here; the left rail (page images) runs at x = 22, the right rail (evidence) at 352
    P = [_defs(pre), hdr(16, 22, "FINDS PAPERS")]
    P.append(_question(16, 34, 328, 84, "narrow"))
    P.append('<path class="cv f-literature-q2" d="M30,118 V144" marker-end="url(#arr)"/>'
             '<text class="lbl f-literature-note" x="40" y="136">up to 5 queries</text>')
    P.append(_chip(16, 148, 160, 30, SOURCES[0][0], False) + _chip(184, 148, 160, 30, SOURCES[1][0], False)
             + _chip(16, 184, 160, 30, SOURCES[2][0], True))
    P.append('<text class="sub f-literature-note" x="190" y="198">merged · ranked</text>'
             '<text class="sub f-literature-note" x="190" y="216">top 5 PDFs</text>')
    P.append(f'<path class="f-literature-flow" d="M180,222 V262" data-t="{FT["merge"]}" opacity="0"/>'
             '<path class="cv f-literature-merge" d="M180,222 V262" marker-end="url(#arr)"/>')
    sx, sy, sw, sh = 126, 268, 108, 150
    P.append(hdr(16, 252, "PDF PAGES"))
    P.append(_stack(pre, sx, sy, sw, sh))
    # text chunks
    y0 = sy + sh + 46
    P.append(_flow(f"M180,{sy + sh + 8} V{y0 - 18}", "text"))
    P.append(hdr(X, y0, "BM25 · TEXT CHUNKS"))
    rows, cut_y = _rows(X, y0 + 14, 344 - X, 34, 28)
    P.append(rows)
    ny = y0 + 14 + 6 * 34 + 14
    P.append(f'<text class="sub f-literature-note" x="{X}" y="{ny}">overlapping chunks</text>'
             f'<text class="sub f-literature-note" x="344" y="{ny}" text-anchor="end">~1,200 chars</text>'
             f'<text class="sub f-literature-note" x="{X}" y="{ny + 20}">top k · ≤ 2 per page</text>')
    # page images, fed down the left rail
    y1 = ny + 64
    P.append(hdr(X, y1, "PAGE IMAGES"))
    ty = y1 + 14
    P.append(_flow(f"M{sx - 2},{sy + 40} C60,{sy + 40} 22,{sy + 40} 22,{sy + 80} V{ty + 21} H{X - 4}", "images"))
    P.append(_thumbs(X, ty, 4, 30, 42, 8))
    P.append(f'<text class="sub f-literature-note" x="344" y="{ty + 17}" text-anchor="end">ColSmol-500M ranks</text>'
             f'<text class="sub f-literature-note" x="344" y="{ty + 37}" text-anchor="end">the page images</text>')
    cy_ = ty + 70
    P.append(_flow(f"M{X + 3 * 38 + 15},{ty + 44} V{cy_ - 4}", "thumbs"))  # from the top-ranked page (rightmost)
    P.append(_chart_page(pre, X, cy_, 344 - X, 140, (344 - 70, cy_ + 76, 36, 150)))
    P.append(_flow(f"M190,{cy_ + 142} V{cy_ + 162}", "chart"))
    rdy = cy_ + 166
    P.append(_reading(X, rdy, 344 - X, 136, " sm"))
    # knowledge graph
    y2 = rdy + 136 + 44
    P.append(hdr(X, y2, "KNOWLEDGE GRAPH · GNN"))
    P.append(f'<text class="sub f-literature-note" x="{X}" y="{y2 + 22}">graph neural network</text>')
    g = y2 + 40
    pts = [(64, g + 34), (296, g + 84), (64, g + 160), (296, g + 212)]
    bg = [(24, g + 100), (150, g + 16), (190, g + 92), (330, g + 140), (176, g + 238), (40, g + 232), (330, g + 24)]
    edges = [(0, 4), (0, 5), (1, 10), (1, 7), (1, 6), (2, 4), (3, 7), (5, 6), (8, 9), (5, 10)]
    P.append(_graph(pts, bg, edges,
                    lbl_pos=[(64, g + 12, "middle"), (344, g + 60, "end"), (64, g + 190, "middle"), (330, g + 242, "end")],
                    rel_pos=[(196, g + 48, "start"), (162, g + 117, "end"), (196, g + 176, "start")]))
    # the language model, fed by the right rail (text chunks, page readings) and the graph path
    py = g + 290
    docks = [(py + 66, "text chunks", KEPT_PAGES, False), (py + 120, "page readings", "[p. 6]", False),
             (py + 174, "graph path", "3 hops", True)]
    bt, bb = y0 + 16, y0 + 14 + 4 * 34 + 26  # bracket over the rows above the cut (the top k)
    P.append(f'<path class="f-literature-brk" d="M347,{bt} H352 V{bb} H347"/>')
    P.append(_flow(f"M352,{bb} V{py + 30} H348", "chunks"))
    P.append(_flow(f"M348,{rdy + 75} H352 V{py + 30} H348", "reading"))
    P.append(_flow(f"M305,{g + 212} C340,{g + 212} 340,{g + 212} 340,{g + 240} V{py - 4}", "graph", dashed=True))
    P.append(f'<text class="lbl f-literature-optlbl" x="330" y="{g + 272}" text-anchor="end">with a graph source</text>')
    P.append(_panel(pre, 16, py, 328, 238, docks, py + 30))
    ay = py + 238 + 44
    P.append(_flow(f"M180,{py + 238} V{ay - 16}", "answer"))
    P.append(_answer(pre, 16, ay, 328, 112, "narrow", 180, tail_up=True))
    H = ay + 112 + 128  # four legend rows below the answer
    P.append("".join(legend([it], 16, H - 84 + 24 * k) for k, it in enumerate(LEGEND)) + note(16, H - 12))
    return svg(W, H, "".join(P), "narrow", LABEL)


JS = """MAFig.register("literature", function (root, variant) {
  var wide = variant === "wide";
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var one = function (s) { return root.querySelector(s); };
  // layout read from the SVG before any from-state is applied
  var lens = one(".f-literature-lens"), mag = one(".f-literature-mag"), travel = +lens.getAttribute("data-travel"),
    S = +lens.getAttribute("data-s"), wipe = one(".f-literature-wipe"), AW = +wipe.getAttribute("width"),
    scan = q(".f-literature-scan > *"), rg = one(".f-literature-scan").getAttribute("data-range").split(" ").map(Number);
  var bars = q(".f-literature-bar"), hops = q(".f-literature-hop"), hopg = q(".f-literature-hopg"),
    walker = one(".f-literature-walker"), xy = q(".f-literature-hopnode").map(function (n) {
      return [+n.getAttribute("cx"), +n.getAttribute("cy")]; });
  gsap.set(bars, {transformOrigin: "0%% 50%%"});
  var intro = gsap.timeline({defaults: {ease: "power3.out"}});
  intro.from(q(".hdr"), {opacity: 0, duration: .5}, 0)
    .from(q(".f-literature-q"), wide ? {opacity: 0, x: -20, duration: .5} : {opacity: 0, y: -12, duration: .5}, .1)
    .from(q(".f-literature-q2, .f-literature-merge"), {drawSVG: 0, opacity: 0, duration: .4, stagger: .05}, .4)
    .from(q(".f-literature-src"), {opacity: 0, y: -8, duration: .35, stagger: .08}, .45)
    .from(q(".f-literature-front"), {opacity: 0, duration: .4}, .7);
  // the back pages fan out from behind the front page
  q(".f-literature-page").forEach(function (p) {
    intro.from(p, {opacity: 0, rotation: -p.getAttribute("data-a"), svgOrigin: p.getAttribute("data-o"), duration: .7,
      ease: "back.out(1.6)"}, .85);
  });
  intro.from(scan, {opacity: 0, duration: .4}, 1.1)
    .from(q(".f-literature-in:not(.f-literature-late)"), {drawSVG: 0, opacity: 0, duration: .5, stagger: .04}, 1.1)
    .from(q(".f-literature-late:not(.f-literature-opt)"), {drawSVG: 0, opacity: 0, duration: .5, stagger: .1}, 2.7)
    // dashed lines fade or scale in: DrawSVG would replace their dash pattern
    .from(q(".f-literature-opt, .f-literature-optlbl"), {opacity: 0, duration: .5}, 2.8)
    .from(q(".f-literature-row"), {opacity: 0, x: -12, duration: .35, stagger: .07}, 1.2)
    .from(bars, {scaleX: 0, duration: .6, stagger: .07}, 1.35)
    .from(q(".f-literature-cut"), {scaleX: 0, transformOrigin: "0%% 50%%", duration: .4}, 1.9)
    .from(q(".f-literature-note"), {opacity: 0, duration: .4, stagger: .03}, 1.5)
    .from(q(".f-literature-thumb"), {opacity: 0, y: 8, duration: .3, stagger: .06}, 1.5)
    .from(q(".f-literature-cpage"), {opacity: 0, duration: .4}, 1.7)
    .from(q(".f-literature-cpage .f-literature-curve"), {drawSVG: 0, duration: .8, ease: "power1.inOut"}, 1.8)
    .from(lens, {opacity: 0, scale: .4, transformOrigin: "50%% 50%%", duration: .5, ease: "back.out(2)"}, 2.2)
    .from(q(".f-literature-read"), wide ? {opacity: 0, x: 16, duration: .4} : {opacity: 0, y: 10, duration: .4}, 2.3)
    .from(q(".f-literature-ge"), {opacity: 0, duration: .4}, 2.0)
    .from(q(".f-literature-gn"), {scale: 0, transformOrigin: "50%% 50%%", duration: .3, stagger: .03}, 2.0)
    .from(hopg, {scale: 0, transformOrigin: "50%% 50%%", duration: .35, stagger: .12, ease: "back.out(2.5)"}, 2.2)
    .from(hops, {drawSVG: 0, duration: .3, stagger: .12, ease: "none"}, 2.35)
    .from(q(".f-literature-badge, .f-literature-ent, .f-literature-rel"), {opacity: 0, duration: .3, stagger: .05}, 2.5)
    .from(q(".f-literature-lm"), {opacity: 0, scale: .96, transformOrigin: "50%% 50%%", duration: .5}, 2.6)
    .from(q(".f-literature-dock"), {opacity: 0, x: -10, duration: .3, stagger: .1}, 2.8)
    .from(q(".f-literature-answer"), {opacity: 0, scale: .92, transformOrigin: wide ? "50%% 100%%" : "50%% 0%%",
      duration: .45, ease: "back.out(2)"}, 3.1)
    .from(wipe, {attr: {width: 0}, duration: .8, ease: "power1.inOut"}, 3.3)
    .from(q(".legend"), {opacity: 0, duration: .4}, 3.4);
  // loop: the beam sweeps the front page, the bars regrow best first, the lens glides along the chart, a walker hops
  // the graph path, the evidence flows to the docks and the answer writes in again. Every key in a fromTo start object
  // is repeated in its end object (a loop wrap drops start-only keys). immediateRender off: the finished frame stays.
  var loop = gsap.timeline({repeat: -1, defaults: {immediateRender: false}});
  loop.fromTo(scan, {y: -rg[0], opacity: 1}, {y: rg[1], opacity: 1, duration: 1.8, ease: "none"}, 0)
    .fromTo(scan, {y: -rg[0], opacity: 0}, {y: 0, opacity: 1, duration: .7, ease: "power2.out"}, 1.85)
    .fromTo(bars, {scaleX: 0}, {scaleX: 1, duration: .6, stagger: .08, ease: "power2.out"}, .7);
  q(".f-literature-flow").forEach(function (el) {
    var t = +el.getAttribute("data-t");
    loop.fromTo(el, {drawSVG: "0%% 14%%", opacity: 1}, {drawSVG: "86%% 100%%", opacity: 1, duration: .6, ease: "power1.in"}, t)
      .to(el, {opacity: 0, duration: .15}, t + .6);
  });
  // the lens glides out along the chart and back (no jump at the loop wrap); the magnified copy counter-moves
  loop.to(lens, {x: -travel, duration: 1.1, ease: "sine.inOut"}, 2.2)
    .to(lens, {x: 0, duration: 1.1, ease: "sine.inOut"}, 3.3)
    .to(mag, {x: travel * S, duration: 1.1, ease: "sine.inOut"}, 2.2)
    .to(mag, {x: 0, duration: 1.1, ease: "sine.inOut"}, 3.3)
    .fromTo(q(".f-literature-rd"), {opacity: .2}, {opacity: 1, duration: .4}, 4.4)
    .fromTo(walker, {x: 0, y: 0, opacity: 0}, {x: 0, y: 0, opacity: 1, duration: .2}, 4.85);
  for (var i = 1; i < xy.length; i++) {
    var t = 5.0 + (i - 1) * .7, dx0 = xy[i - 1][0] - xy[0][0], dy0 = xy[i - 1][1] - xy[0][1];
    loop.fromTo(walker, {x: dx0, y: dy0, opacity: 1}, {x: xy[i][0] - xy[0][0], y: xy[i][1] - xy[0][1], opacity: 1,
        duration: .6, ease: "power1.inOut"}, t)
      .fromTo(hops[i - 1], {drawSVG: "0%%"}, {drawSVG: "100%%", duration: .6, ease: "power1.inOut"}, t)
      .fromTo(hopg[i], {scale: 1}, {scale: 1.3, transformOrigin: "50%% 50%%", duration: .15, yoyo: true, repeat: 1}, t + .6);
  }
  loop.to(walker, {opacity: 0, duration: .25}, 7.2)
    .fromTo(q(".f-literature-dock"), {opacity: .4}, {opacity: 1, duration: .3, stagger: .15}, 7.5)
    .fromTo(wipe, {attr: {width: 0}}, {attr: {width: AW}, duration: 1.1, ease: "power1.inOut"}, 8.3)
    .set({}, {}, %(TL)s);
  return {intro: intro, loop: loop};
});""" % {"TL": T_LOOP}

# every loop event ends inside the loop period (answer wipe 8.3 + 1.1; last flow + .75)
assert 8.3 + 1.1 <= T_LOOP and max(FT.values()) + .75 <= T_LOOP


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
