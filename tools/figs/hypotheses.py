"""Hypotheses figure: a hypothesis machine. Retrieval feeds screened inspirations to seven generator nozzles (C12,
C56); a swarm of candidates pours into a funnel of hard checks whose failures deflect down an amber chute (C13-C15);
the survivors sit under an evidence lens in the language model's panel (the one dark panel), where quoted verdicts
and the critic's flaw meter reject a few more (C16); near-duplicates go, the rest take seats in a blinded
both-order tournament (C17, C57) and Bradley-Terry bars grow with bootstrap intervals before the rows settle into the
final order. The SVG is the finished frame (every particle at rest); the GSAP intro and loop replay one pass, and no
verdict, colour, game or rank shows before the step that decides it."""
import math
from html import escape

from figkit import Figure, curve_d, f, hdr, icon, legend, note, svg

# ---------------------------------------------------------------- illustrative data
SOURCES = [("Paper search", "≤ 10 per query"), ("Knowledge base", "≤ 8 per query"),
           ("Materials Project", "baseline formula")]
# tier label, then (generator, sub-label, queries the database)
TIERS = [("quick", [("inspiration", "screened inspirations", False)]),
         ("standard adds", [("assumption hop", "assumptions, if-then", False),
                            ("analogy", "neighbouring domains", False)]),
         ("deep adds", [("database pattern", "patterns in records", True),
                        ("anomaly detection", "outliers ≥ 2.5 SD", True),
                        ("trend extrapolation", "line fit per property", True),
                        ("contradiction resolution", "LCA agreement map", False)])]
N_GEN, PER_GEN = 7, 4  # illustrative; deep asks each generator twice for four (up to eight), then merges (C57)
CHECKS = ["schema", "elements", "≠ baseline", "answers the goal", "hard constraints", "SMILES · RDKit", "IZA code",
          "Si/Al ≥ 1", "Σ ≤ 101 %"]
VERDICTS = [("supports", True), ("already explained", False), ("other more likely", False),
            ("missing piece", False), ("neutral", False), ("disproved", True)]  # True: stands only with a quote
SEVERITY = ["minor", "major", "fatal"]
# particle n comes from generator n % 7; its fate: ("seat", s) | ("hard", check row) | ("dis",) | ("fatal",) | ("dup",)
FATES = [("seat", 0), ("hard", 1), ("seat", 1), ("hard", 5), ("dup",), ("hard", 7), ("seat", 2),
         ("hard", 0), ("dis",), ("seat", 3), ("hard", 6), ("hard", 8), ("seat", 4), ("hard", 2),
         ("hard", 4), ("dup",), ("fatal",), ("seat", 5), ("hard", 3), ("hard", 5), ("seat", 6),
         ("dis",), ("hard", 7), ("dup",), ("hard", 4), ("fatal",), ("seat", 7), ("hard", 6)]
N_SEAT = 8
N_HARD = sum(x[0] == "hard" for x in FATES)  # rest slots in the trays
N_REV = sum(x[0] in ("dis", "fatal") for x in FATES)
# games between seats (i < j, 0-based): winner seat, "t" tie, "x" failed and excluded; pairs not listed were not paired
GAMES = {(0, 1): 0, (0, 2): 2, (0, 3): 0, (0, 5): "t", (0, 7): 0, (1, 2): 2, (1, 3): 1, (1, 4): 1, (1, 6): "x",
         (1, 7): "t", (2, 3): 2, (2, 4): 2, (2, 5): 2, (2, 7): 2, (3, 4): "t", (3, 6): 3, (4, 5): 5, (4, 6): 6,
         (5, 6): 5, (5, 7): 5, (6, 7): 7}
# Bradley-Terry log-strength and its bootstrap interval: HF/pipeline/rank.py's bradley_terry and bootstrap_ci
# (alpha 0.1, 200 resamples, random.Random(0)) run on GAMES in this dict order, failed game left out (numpy 1.21.6);
# refit if GAMES changes. Critic score and soft-check failures are illustrative.
BT = [(1.07, .25, 1.95), (-.01, -.97, .79), (2.4, 1.05, 2.86), (-.9, -1.71, .15), (-1.71, -2.53, -.49),
      (.87, .02, 1.45), (-1.34, -2.37, .29), (-.38, -1.32, .34)]
CRITIC = [5, 4, 4, 3, 3, 4, 2, 3]
SOFT = [0, 0, 0, 1, 0, 1, 0, 0]
BT_MAX = 3.0  # strength axis runs -3..+3


def _final_order():
    """Seats in final order: critic score first, then soft-check failures, then strength (flaws equal here)."""
    return sorted(range(N_SEAT), key=lambda s: (-CRITIC[s], SOFT[s], -BT[s][0]))


ORDER = _final_order()


def _score(s):
    pts = 0.0
    for (i, j), r in GAMES.items():
        if s in (i, j) and r != "x":
            pts += .5 if r == "t" else float(r == s)
    return pts


# the fitted strengths follow the game results (a check on the hand-copied fit)
assert sorted(range(N_SEAT), key=lambda s: -BT[s][0])[:3] == sorted(range(N_SEAT), key=lambda s: -_score(s))[:3]
assert ORDER[0] != max(range(N_SEAT), key=lambda s: BT[s][0])  # the critic outranks strength in the figure
assert sum(1 for x in FATES if x[0] == "seat") == N_SEAT and len(FATES) == N_GEN * PER_GEN

LABEL = ("Hypothesis machine. Before generation, paper search (up to 10 results per query), the knowledge base (up "
         "to 8) and Materials Project (a baseline formula) are queried, and a language model screens the results into "
         "inspirations. All seven generators run, each a language-model prompt: inspiration at quick effort; "
         "assumption hop and analogy added at standard; and at deep, where each generator is asked twice and the "
         "results are merged, database pattern, anomaly detection (values at least 2.5 standard deviations from the mean, by default) and trend extrapolation, "
         "which query the database's records, and contradiction resolution, from an LCA agreement map. Candidates "
         "pour into rule-based gates: schema, element symbols, not the baseline, answering the goal, hard "
         "constraints, and domain checks (SMILES sanitised by RDKit, a valid IZA code, Si/Al at least 1, a "
         "composition summing to at most 101 %). A candidate that fails a hard check is rejected; a domain check "
         "with no identifier gives unknown, never a failure, and soft checks only lower the rank. A language model "
         "reviews each remaining candidate against up to eight retrieved passages; supports and disproved stand only "
         "with a verbatim quote, and a quoted disproved rejects. A critic rates flaws minor, major or fatal, giving a "
         "score from 1 to 5; a fatal flaw rejects unless none would remain. Near-duplicates are removed, then a judge "
         "that sees no IDs, generator or lineage compares pairs in both presentation orders: a pair is won only if "
         "won in both, a split is a tie, and failed games are excluded. At deep effort each candidate plays its most "
         "similar ones, up to 150 pairs, and the top three also debate. A Bradley–Terry model is fitted to the games with bootstrap intervals, and "
         "the final order puts gate, critic score, flaws and soft checks ahead of strength. The candidates, games, "
         "scores and strengths are illustrative.")
LEGEND = [("dot", "candidate"), ("adot", "rejected"), ("cell", "not paired"), ("dash", "game failed: excluded")]

# ---------------------------------------------------------------- timing (s from the start of a pass; both variants)
EMIT0, EMIT_DT = .4, .045
LEG = {"mouth": .2, "check": .32, "slot": .2, "chute": .4, "rest": .3, "neck": .3, "lens": .35,
       "out": .45, "tray2": .45, "lane": .6, "dedup": .25, "seat": .4}
NONHARD = [n for n, x in enumerate(FATES) if x[0] != "hard"]
R0 = EMIT0 + EMIT_DT * NONHARD[-1] + LEG["mouth"] + LEG["check"] + LEG["neck"] + LEG["lens"] + .2  # review starts
SCAN = .9
CHIP_T = [round(R0 + .12 + .09 * i, 3) for i in range(len(VERDICTS))]
SEV_T = [round(R0 + .8 + .1 * i, 3) for i in range(3)]
X0 = round(R0 + 1.25, 3)  # the lens empties
EXIT_DT = .045
SEAT_T = X0 + EXIT_DT * (len(NONHARD) - 1) + LEG["out"] + LEG["lane"] + LEG["dedup"] + LEG["seat"]
G0 = round(SEAT_T + .25, 3)  # pairs drawn
CELL_DT = .04
# the game card: order 1, the swap, order 2, the rule lines, the swap back (one clock with the cells)
GAME_T = {"o1": round(G0 + .05, 3), "swap": round(G0 + .25, 3), "o2": round(G0 + .7, 3), "rule": round(G0 + .95, 3),
          "back": round(G0 + 1.3, 3)}
B0 = round(G0 + .35 + CELL_DT * len(GAMES) + .3, 3)  # bars grow
SORT_T, RANK_T = round(B0 + .75, 3), round(B0 + 1.35, 3)
PASS_END = RANK_T + .3
HOLD = 2.2  # loop: the finished frame holds, then clears, then a pass replays
T0_LOOP = HOLD + .9
T_LOOP = round(T0_LOOP + PASS_END + .1, 3)
T0_INTRO = 1.0

assert CHIP_T[-1] < SEV_T[0] < SEV_T[-1] + .1 < X0  # verdicts, then the critic, then the lens empties


def _te(n):
    return round(EMIT0 + EMIT_DT * n, 3)


# ---------------------------------------------------------------- geometry helpers
def _cub(p0, p1, p2, p3, k=6):
    """k points along a cubic Bezier, after p0."""
    out = []
    for i in range(1, k + 1):
        t = i / k
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def _hcurve(p, q, k=6):
    dx = max(abs(q[0] - p[0]) * .5, 12) * (1 if q[0] >= p[0] else -1)
    return _cub(p, (p[0] + dx, p[1]), (q[0] - dx, q[1]), q, k)


def _vcurve(p, q, k=6):
    dy = max(abs(q[1] - p[1]) * .5, 12) * (1 if q[1] >= p[1] else -1)
    return _cub(p, (p[0], p[1] + dy), (q[0], q[1] - dy), q, k)


def _sun(cx, cy, r, n):
    """n spots filling a disc of radius r (a sunflower spiral)."""
    return [(cx + r * math.sqrt((j + .5) / n) * math.cos(j * 2.39996), cy + r * math.sqrt((j + .5) / n) * math.sin(j * 2.39996))
            for j in range(n)]


def _walk(t, start, legs):
    """Waypoints [(t, x, y)]: each leg (duration, points) spends its duration over its points by distance."""
    wp, cur = [(t, start[0], start[1])], start
    for dur, pts in legs:
        seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip([cur] + pts, pts)]
        tot = sum(seg)
        for p, d in zip(pts, seg):
            t += dur * (d / tot if tot else 1 / len(pts))  # a leg that stays put (a wait) still takes its time
            wp.append((round(t, 3), round(p[0], 1), round(p[1], 1)))
        cur = pts[-1]
    return wp


def _particles(G):
    """Every candidate's path through the machine for one variant's geometry G. Returns the particle markup and
    the stage times (asserted equal across variants)."""
    out, lens_j, hard_i, rev_i = [], {}, 0, 0
    lens_spots = G["lens_spots"](len(NONHARD))
    for j, n in enumerate(NONHARD):
        lens_j[n] = j
    seat_arrive, dup_t = [], []
    for n, fate in enumerate(FATES):
        g = n % N_GEN
        te, kind = _te(n), fate[0]
        legs = [(LEG["mouth"], G["enter"](g, n)), (LEG["check"], [G["check"](fate, n)])]
        amber = fade = row = None
        if kind == "hard":
            row = fate[1]
            amber = round(te + LEG["mouth"] + LEG["check"], 3)
            legs += [(LEG["slot"], G["slot"](G["check"](fate, n))), (LEG["chute"], G["chute"]()),
                     (LEG["rest"], [G["rest"](hard_i)])]
            hard_i += 1
            rest = G["rest"](hard_i - 1)
        else:
            j = lens_j[n]
            legs += [(LEG["neck"], G["neck"](n)), (LEG["lens"], G["lens_in"](lens_spots[j]))]
            wp = _walk(te, G["nozzle"](g), legs)
            arrive, hold_t = wp[-1][0], X0 + EXIT_DT * j
            legs.append((round(hold_t - wp[-1][0], 3), [lens_spots[j]]))  # waits under the lens
            legs.append((LEG["out"], G["lens_out"](lens_spots[j])))
            if kind in ("dis", "fatal"):
                amber = CHIP_T[-1] + .05 if kind == "dis" else SEV_T[-1] + .05
                legs.append((LEG["tray2"], G["tray2"](rev_i)))
                rest = G["tray2"](rev_i)[-1]
                rev_i += 1
            else:
                legs.append((LEG["lane"], G["lane"]()))
                legs.append((LEG["dedup"], [G["dedup"]]))
                if kind == "dup":
                    rest = None
                else:
                    legs.append((LEG["seat"], G["seat"](fate[1])))
                    rest = G["seat"](fate[1])[-1]
        wp = _walk(te, G["nozzle"](g), legs)
        if kind == "dup":
            fade = wp[-1][0]
            dup_t.append(fade)
        if kind == "seat":
            seat_arrive.append((fate[1], wp[-1][0]))
        if kind == "hard":  # turns amber at the check it fails, not before
            assert any(abs(t - amber) < 1e-6 for t, *_ in wp), (n, amber)
        elif amber is not None:
            assert arrive < amber < hold_t, (n, arrive, amber, hold_t)  # decided under the lens, while it waits there
        x, y = rest if rest else wp[-1][1:]
        amb = kind != "seat" and kind != "dup"
        data = " ".join(f"{t:g}:{px:g}:{py:g}" for t, px, py in wp)
        a = f' data-a="{amber:g}"' if amber is not None else ""
        r = f' data-r="{row}"' if row is not None else ""
        o = f' data-o="{fade:g}"' if fade is not None else ""
        vis = ' opacity="0"' if kind == "dup" else ""
        hide = ' opacity="0"'
        out.append(f'<g class="f-hypotheses-pt" transform="translate({f(x)},{f(y)})" data-g="{g}" data-p="{data}"{a}{r}{o}{vis}>'
                   f'<circle class="f-hypotheses-ptc" r="3.6"{hide if amb else ""}/>'
                   f'<circle class="f-hypotheses-pta" r="3.6"{"" if amb else hide}/></g>')
    seat_t = dict(seat_arrive)
    assert max(seat_t.values()) <= G0 - .2 + 1e-6, max(seat_t.values())
    return "".join(out), seat_t, dup_t


# ---------------------------------------------------------------- components
def _defs(pre):
    return (f'<defs><linearGradient id="{pre}-pnl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="f-hypotheses-g0"/>'
            f'<stop offset="1" class="f-hypotheses-g1"/></linearGradient>'
            f'<filter id="{pre}-glow" x="-1" y="-1" width="3" height="3"><feGaussianBlur stdDeviation="1.8" result="g"/>'
            f'<feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')


def _src(x, y, w, h, title, sub, inline):
    if inline:
        t = (f'<text class="ttl sm" x="{f(x + 14)}" y="{f(y + h / 2 + 5)}">{escape(title)}</text>'
             f'<text class="sub" x="{f(x + w - 12)}" y="{f(y + h / 2 + 4.5)}" text-anchor="end">{escape(sub)}</text>')
    else:
        t = (f'<text class="ttl sm" x="{f(x + 14)}" y="{f(y + 19)}">{escape(title)}</text>'
             f'<text class="sub" x="{f(x + 14)}" y="{f(y + 36)}">{escape(sub)}</text>')
    return f'<g class="card f-hypotheses-src"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="8"/>{t}</g>'


def _gen(x, y, w, h, name, sub, db, g, tier=None):
    """Generator card with its nozzle; tier (narrow): the lowest effort that runs it, as a tag on the title line,
    which moves the database icon down to the sub-label line."""
    ic = icon("memory", x + w - 24, y + (21 if tier else 13), "ic f-hypotheses-db") if db else ""
    tg = f'<text class="tag" x="{f(x + w - 12)}" y="{f(y + 17)}" text-anchor="end">{tier}</text>' if tier else ""
    cy = y + h / 2
    return (f'<g class="card f-hypotheses-gen"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="9"/>'
            f'<text class="ttl sm" x="{f(x + 14)}" y="{f(y + 17)}">{escape(name)}</text>'
            f'<text class="sub" x="{f(x + 14)}" y="{f(y + 36)}">{escape(sub)}</text>{ic}{tg}'
            f'<path class="f-hypotheses-noz" d="M{f(x + w)},{f(cy - 7)} L{f(x + w + 10)},{f(cy - 4)} V{f(cy + 4)} L{f(x + w)},{f(cy + 7)} Z"/>'
            f'<circle class="f-hypotheses-nglow" cx="{f(x + w + 11)}" cy="{f(cy)}" r="7" opacity="0" data-g="{g}"/></g>')


def _check(x, y, text):
    """One hard check: a tick badge (and the amber cross that flashes when a candidate fails it) and its name."""
    return (f'<g class="f-hypotheses-chk"><circle cx="{f(x)}" cy="{f(y - 4.5)}" r="6.5"/>'
            f'<path d="M{f(x - 3.2)},{f(y - 4.5)} l2.2,2.3 l4.1,-4.5"/>'
            f'<g class="f-hypotheses-fl" opacity="0"><circle cx="{f(x)}" cy="{f(y - 4.5)}" r="7.5"/>'
            f'<path d="M{f(x - 3)},{f(y - 7.5)} l6,6 m0,-6 l-6,6"/></g>'
            f'<text class="sub f-hypotheses-ck" x="{f(x + 13)}" y="{f(y)}">{escape(text)}</text></g>')


def _tray(x, y, w, h, tag_x, tag_y):
    return (f'<g class="f-hypotheses-tray"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
            f'<text class="tag f-hypotheses-tt" x="{f(tag_x)}" y="{f(tag_y)}">REJECTED</text></g>')


def _lens(pre, cx, cy, r, handle):
    """Evidence lens over up to eight passages: quote spans (revealed with the verdicts) and the scan bar."""
    P = [f'<g class="f-hypotheses-lens"><circle class="f-hypotheses-glass" cx="{f(cx)}" cy="{f(cy)}" r="{r}"/>']
    for k in range(8):
        yy = cy - r + 14 + k * (2 * r - 28) / 7
        half = math.sqrt(max(r * r - (yy - cy) ** 2, 0)) - 10
        P.append(f'<path class="f-hypotheses-psg" d="M{f(cx - half)},{f(yy)} H{f(cx + half * (.55 if k % 3 == 1 else .9))}"/>')
        if k in (2, 5):
            P.append(f'<path class="f-hypotheses-qh{" amb" if k == 5 else ""}" d="M{f(cx - half * .4)},{f(yy)} '
                     f'H{f(cx + half * .35)}" data-t="{CHIP_T[0] if k == 2 else CHIP_T[-1]}"/>')
    P.append(f'<clipPath id="{pre}-lc"><circle cx="{f(cx)}" cy="{f(cy)}" r="{r - 2}"/></clipPath>'
             f'<g clip-path="url(#{pre}-lc)"><rect class="f-hypotheses-scan" x="{f(cx - r)}" y="{f(cy - r)}" '
             f'width="{2 * r}" height="12" opacity="0" data-t="{R0}" data-dy="{2 * r - 12}"/></g>')
    hx, hy, ex, ey = handle
    P.append(f'<path class="f-hypotheses-handle" d="M{f(hx)},{f(hy)} L{f(ex)},{f(ey)}"/>'
             f'<circle class="f-hypotheses-ring" cx="{f(cx)}" cy="{f(cy)}" r="{r}"/></g>')
    return "".join(P)


def _verdicts(x, y, w, pitch):
    P = []
    for i, (v, quoted) in enumerate(VERDICTS):
        yy = y + i * pitch
        amb = " amb" if v == "disproved" else ""
        P.append(f'<g class="f-hypotheses-vd{amb}"><rect x="{f(x)}" y="{f(yy)}" width="{f(w)}" height="22" rx="11"/>'
                 f'<text class="sub f-hypotheses-vt" x="{f(x + 12)}" y="{f(yy + 15.5)}">{escape(v)}</text>'
                 f'<rect class="f-hypotheses-vp{amb}" x="{f(x - 2)}" y="{f(yy - 2)}" width="{f(w + 4)}" height="26" rx="13" '
                 f'opacity="0" data-t="{CHIP_T[i]}"/></g>')
        if quoted:
            P.append(f'<text class="f-hypotheses-qg{amb}" x="{f(x - 6)}" y="{f(yy + 20)}" text-anchor="end">“</text>')
    return "".join(P)


def _critic(x, y, bw, gap):
    P = [f'<text class="tag f-hypotheses-ptag" x="{f(x)}" y="{f(y)}">CRITIC · FLAWS</text>']
    for i, s in enumerate(SEVERITY):
        bx = x + i * (bw + gap)
        amb = " amb" if s == "fatal" else ""
        P.append(f'<g class="f-hypotheses-sev{amb}"><rect x="{f(bx)}" y="{f(y + 12)}" width="{f(bw)}" height="26" rx="6"/>'
                 f'<text class="sub f-hypotheses-on" x="{f(bx + bw / 2)}" y="{f(y + 29.5)}" text-anchor="middle">{s}</text>'
                 f'<rect class="f-hypotheses-cs{amb}" x="{f(bx)}" y="{f(y + 12)}" width="{f(bw)}" height="26" rx="6" '
                 f'opacity="0" data-t="{SEV_T[i]}"/></g>')
    return "".join(P)


def _panel_head(pre, x, y, w, h, tx, ty, subs):
    return (f'<rect class="panel" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="14" style="fill:url(#{pre}-pnl)"/>'
            f'{icon("augment", tx, ty - 14, "ic f-hypotheses-pic")}'
            f'<text class="f-hypotheses-lmt" x="{f(tx + 26)}" y="{f(ty)}">Language model</text>'
            + "".join(f'<text class="sub f-hypotheses-on" x="{f(tx)}" y="{f(ty + 22 + 20 * k)}">{escape(t)}</text>'
                      for k, t in enumerate(subs)))


def _dedup(cx, cy, times):
    """Two overlapping candidates; one pulse ring per removed near-duplicate, at the time it is removed."""
    return (f'<g class="f-hypotheses-dd"><circle cx="{f(cx - 12)}" cy="{f(cy)}" r="20"/><circle cx="{f(cx + 12)}" cy="{f(cy)}" r="20"/>'
            + "".join(f'<circle class="f-hypotheses-ddp" cx="{f(cx)}" cy="{f(cy)}" r="30" opacity="0" data-t="{t}"/>' for t in times)
            + '</g>')


def _table(x0, y0, c, seat_t):
    """Crosstable: seats (row headers with docking sockets), column heads, played cells resolving to a winner, a
    tie or an excluded game; blank cells were not paired."""
    P = []
    for i in range(N_SEAT):
        cy = y0 + i * c + c / 2
        P.append(f'<g class="f-hypotheses-seat"><circle class="f-hypotheses-sock" cx="{f(x0 - 36)}" cy="{f(cy)}" r="7"/>'
                 f'<circle class="f-hypotheses-sockp" cx="{f(x0 - 36)}" cy="{f(cy)}" r="11" opacity="0" data-t="{seat_t[i]}"/>'
                 f'<text class="sub f-hypotheses-hid" x="{f(x0 - 4)}" y="{f(cy + 4.5)}" text-anchor="end">H{i + 1}</text></g>')
        P.append(f'<text class="sub f-hypotheses-hid" x="{f(x0 + i * c + c / 2)}" y="{f(y0 - 8)}" text-anchor="middle">H{i + 1}</text>')
    m = 0
    for i in range(N_SEAT):
        P.append(f'<rect class="f-hypotheses-diag" x="{f(x0 + i * c + 3)}" y="{f(y0 + i * c + 3)}" width="{c - 6}" height="{c - 6}" rx="3"/>')
        for j in range(i + 1, N_SEAT):
            x, y = x0 + j * c, y0 + i * c
            r = GAMES.get((i, j))
            P.append(f'<rect class="f-hypotheses-cell" x="{f(x + 2)}" y="{f(y + 2)}" width="{c - 4}" height="{c - 4}" rx="4"/>')
            if r is None:
                continue
            t = round(G0 + .35 + CELL_DT * m, 3)
            m += 1
            cx, cy = x + c / 2, y + c / 2
            if r == "x":
                # paired like any other; only its outcome (a dashed stroke, as in the legend) says the game failed
                P.append(f'<rect class="f-hypotheses-frame" x="{f(x + 2)}" y="{f(y + 2)}" width="{c - 4}" height="{c - 4}" rx="4" data-t="{G0}"/>'
                         f'<path class="f-hypotheses-out f-hypotheses-xo" d="M{f(cx - 8)},{f(cy)} h16" data-t="{t}"/>')
                continue
            win = r != "t"
            tint = (f'<rect class="f-hypotheses-out f-hypotheses-wf" x="{f(x + 2)}" y="{f(y + 2)}" width="{c - 4}" '
                    f'height="{c - 4}" rx="4" data-t="{t}"/>' if win else "")
            P.append(f'<rect class="f-hypotheses-frame" x="{f(x + 2)}" y="{f(y + 2)}" width="{c - 4}" '
                     f'height="{c - 4}" rx="4" data-t="{G0}"/>{tint}'
                     f'<path class="f-hypotheses-swap" d="M{f(cx - 6)},{f(cy - 3)} h12 l-3,-3 M{f(cx + 6)},{f(cy + 3)} h-12 l3,3" '
                     f'opacity="0" data-t="{t}"/>'
                     f'<text class="sub f-hypotheses-out{" w" if win else ""}" x="{f(cx)}" y="{f(cy + 4.5)}" text-anchor="middle" '
                     f'data-t="{t}">{"H%d" % (r + 1) if win else "tie"}</text>')
    assert m == len(GAMES)
    return "".join(P)


def _game(x, y, w, side=False):
    """One game, both orders: candidate X and Y swap slots A and B between the two judge calls. side: the order
    lines sit beside the chips (narrow) instead of under them."""
    sw, sh, gap = 54, 38, 14
    ax = x + 14 if side else x + (w - 2 * sw - gap) / 2
    bx = ax + sw + gap
    cy = y + 34

    def chip(cx, cls):
        return (f'<g class="f-hypotheses-gc {cls}" data-dx="{f((bx - ax) if cls == "gx" else (ax - bx))}">'
                f'<rect x="{f(cx)}" y="{f(cy)}" width="{sw}" height="{sh}" rx="6"/>'
                f'<path d="M{f(cx + 8)},{f(cy + 11)} h{sw - 18} M{f(cx + 8)},{f(cy + 19)} h{sw - 24} M{f(cx + 8)},{f(cy + 27)} h{sw - 20}"/></g>')
    lines = [("order 1 → picks A", GAME_T["o1"]), ("order 2 → picks B", GAME_T["o2"]),
             ("same candidate: win", GAME_T["rule"]), ("split → tie", GAME_T["rule"])]
    lx, ly = (bx + sw + 16, y + 30) if side else (x + 12, cy + sh + 40)
    h = 104 if side else sh + 146
    P = [f'<g class="card f-hypotheses-game"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{h}" rx="10"/>'
         f'<text class="tag" x="{f(x + 12)}" y="{f(y + 22)}">BOTH ORDERS</text>',
         chip(ax, "gx"), chip(bx, "gy"),
         f'<text class="tag" x="{f(ax + sw / 2)}" y="{f(cy + sh + 16)}" text-anchor="middle">A</text>'
         f'<text class="tag" x="{f(bx + sw / 2)}" y="{f(cy + sh + 16)}" text-anchor="middle">B</text>']
    for k, (s, t) in enumerate(lines):
        P.append(f'<text class="sub f-hypotheses-go" x="{f(lx)}" y="{f(ly + 19 * k)}" data-t="{t}">{escape(s)}</text>')
    return "".join(P) + "</g>"


def _bars(x_id, x_crit, x_soft, zx, scale, y0, pitch, seat_t):
    """Leaderboard rows, placed in final order; each row carries data-dy back to its seat order. The rank numbers
    sit outside the rows."""
    P = []
    for pos, s in enumerate(ORDER):
        y = y0 + pos * pitch
        v, lo, hi = BT[s]
        bx, bw = (zx, v * scale) if v >= 0 else (zx + v * scale, -v * scale)
        by = y - 10
        soft = " amb" if SOFT[s] else ""
        meta = (f'<text class="sub f-hypotheses-hid" x="{f(x_id)}" y="{f(y)}">H{s + 1}</text>'
                f'<text class="sub" x="{f(x_crit)}" y="{f(y)}" text-anchor="middle">{CRITIC[s]}</text>'
                f'<text class="sub{soft}" x="{f(x_soft)}" y="{f(y)}" text-anchor="middle">{SOFT[s]}</text>')
        ciy = by + 6
        ci = (f'<path class="f-hypotheses-ci" d="M{f(zx + lo * scale)},{f(ciy)} H{f(zx + hi * scale)} '
              f'M{f(zx + lo * scale)},{f(ciy - 5)} v10 M{f(zx + hi * scale)},{f(ciy - 5)} v10" data-t="{round(B0 + .45, 3)}"/>')
        P.append(f'<g class="f-hypotheses-row" data-t="{seat_t[s]}" data-dy="{(s - pos) * pitch}">{meta}'
                 f'<rect class="f-hypotheses-bar{" neg" if v < 0 else ""}" x="{f(bx)}" y="{f(by)}" width="{f(bw)}" height="12" rx="3" '
                 f'data-t="{round(B0 + .05 * pos, 3)}" data-z="{f(zx)}"/>{ci}</g>')
    return "".join(P)


def _axis(zx, scale, y_top, y_bot, label_y):
    P = [f'<path class="f-hypotheses-zero" d="M{f(zx)},{f(y_top)} V{f(y_bot)}"/>']
    for t in (-2, 0, 2):
        x = zx + t * scale
        P.append(f'<path class="f-hypotheses-tick" d="M{f(x)},{f(y_bot)} v5"/>'
                 f'<text class="sub" x="{f(x)}" y="{f(label_y)}" text-anchor="middle">{"%+d" % t if t else "0"}</text>')
    return "".join(P)


def _rank_nums(x, y0, pitch):
    return "".join(f'<text class="sub f-hypotheses-rk" x="{f(x)}" y="{f(y0 + pos * pitch)}" data-t="{RANK_T}">{pos + 1}</text>'
                   for pos in range(N_SEAT))


def _flow(d, t, arrow=False):
    m = ' marker-end="url(#arr)"' if arrow else ""
    return f'<path class="cv f-hypotheses-in" d="{d}"{m}/><path class="f-hypotheses-flow" d="{d}" data-t="{t}" opacity="0"/>'


# ---------------------------------------------------------------- wide
WIDE = {"W": 1100, "H": 1112}
FUN_W = {"x0": 476, "top0": 62, "bot0": 470, "x1": 690, "top1": 246, "bot1": 286}


def _fun_edges(F, x):
    """Upper and lower funnel edge y at x (wide, horizontal funnel)."""
    t = (x - F["x0"]) / (F["x1"] - F["x0"])
    return F["top0"] + t * (F["top1"] - F["top0"]), F["bot0"] + t * (F["bot1"] - F["bot0"])


def _wide():
    W, H, pre = WIDE["W"], WIDE["H"], "hypotheses-w"
    F = FUN_W
    P = [_defs(pre), hdr(30, 34, "RETRIEVE"), hdr(240, 34, "GENERATORS"), hdr(476, 34, "SCREEN · HARD CHECKS"),
         hdr(726, 34, "REVIEW")]
    # retrieval and inspirations; the comb on the left feeds the inspirations card, the bus feeds every generator
    for k, (t, s) in enumerate(SOURCES):
        P.append(_src(30, 48 + 52 * k, 172, 44, t, s, False))
    P.append(f'<path class="cv f-hypotheses-in" d="M30,70 H20 M30,122 H20 M30,174 H20 M20,70 V246 H26" marker-end="url(#arr)"/>')
    P.append(_src(30, 224, 172, 44, "Inspirations", "model-screened", False))
    gens, y = [], 56
    for tier, items in TIERS:
        P.append(f'<text class="lbl f-hypotheses-tier" x="240" y="{y}">{escape(tier)}</text>')
        y += 8
        for name, sub, db in items:
            gens.append((y, name, sub, db))
            y += 50
        y += 22 - 50 + 44
    mids = [gy + 22 for gy, *_ in gens]
    P.append(_flow(f"M202,246 C214,246 214,246 226,246 V{mids[0]}", .05) + _flow(f"M226,246 V{mids[-1]}", .05))
    P += [f'<path class="cv f-hypotheses-in" d="M226,{m} H238" marker-end="url(#arr)"/>' for m in mids]
    for g, (gy, name, sub, db) in enumerate(gens):
        P.append(_gen(240, gy, 208, 44, name, sub, db, g))
    # effort caps under the inspirations
    P.append('<g class="card f-hypotheses-eff"><rect x="30" y="300" width="172" height="112" rx="9"/>'
             '<text class="tag" x="44" y="322">EFFORT CAPS</text>'
             '<text class="lbl" x="44" y="342">quick / standard / deep</text>'
             '<text class="sub" x="44" y="362">calls ≤ 24/150/400</text>'
             '<text class="sub" x="44" y="382">s ≤ 300/1,200/3,600</text>'
             '<text class="lbl" x="44" y="400">retrieval not counted</text></g>')
    # funnel of hard checks
    P.append(f'<path class="f-hypotheses-funnel" d="M{F["x0"]},{F["top0"]} L{F["x1"]},{F["top1"]} L{F["x1"]},{F["bot1"]} '
             f'L{F["x0"]},{F["bot0"]} Z"/><path class="f-hypotheses-rim" d="M{F["x0"]},{F["top0"]} V{F["bot0"]}"/>')
    rows_y = [180 + 24 * k for k in range(len(CHECKS))]
    for yy, c in zip(rows_y, CHECKS):
        end = 512 + len(c) * 7.7
        top, bot = _fun_edges(F, end)
        assert top < yy - 11 and yy + 4 < bot, (c, top, bot)  # each check sits inside the funnel
        P.append(_check(498, yy, c))
    slot = (650, _fun_edges(F, 650)[1])
    tray_x, tray_y, tray_w, tray_h = 476, 596, 244, 56
    P.append(f'<path class="cv f-hypotheses-rej" d="M{f(slot[0])},{f(slot[1])} C660,420 700,500 700,{tray_y - 2}" marker-end="url(#arr)"/>')
    for k, s in enumerate(["missing identifier → unknown,", "never a failure", "soft checks never reject:",
                           "they only lower the rank"]):
        P.append(f'<text class="lbl f-hypotheses-fn" x="480" y="{500 + 18 * k + (10 if k > 1 else 0)}">{escape(s)}</text>')
    P.append(_tray(tray_x, tray_y, tray_w, tray_h, 490, 629))
    rest = [(572 + 16 * (i % 9), 614 + 20 * (i // 9)) for i in range(N_HARD + N_REV)]
    assert N_HARD + N_REV <= 18  # two rows of nine
    # the language model: lens, verdicts, critic
    px, py, pw, ph = 726, 56, 344, 424
    lx, ly, lr = 820, 214, 60
    P.append('<g class="f-hypotheses-lm">' + _panel_head(pre, px, py, pw, ph, 748, 87, ["reviews · ≤ 8 passages"]))
    P.append(_lens(pre, lx, ly, lr, (lx + 42, ly + 42, lx + 58, ly + 58)))
    P.append(_verdicts(904, 134, 154, 28))
    P.append(f'<text class="lbl f-hypotheses-pl" x="748" y="322">“supports” and “disproved” need a verbatim quote;</text>'
             f'<text class="lbl f-hypotheses-pl" x="748" y="340">otherwise neutral · a quoted “disproved” rejects</text>')
    P.append(_critic(748, 378, 80, 8))
    P.append(f'<text class="sub f-hypotheses-on" x="1012" y="407">→ 1–5</text>'
             f'<text class="lbl f-hypotheses-pl" x="748" y="446">a fatal flaw rejects, unless none would remain</text></g>')
    P.append(f'<path class="cv f-hypotheses-in" d="{curve_d(F["x1"], 266, lx - lr - 4, ly + 12)}" marker-end="url(#arr)"/>')
    P.append(f'<path class="cv f-hypotheses-in" d="M{lx - 44},{ly + 46} C750,290 736,300 736,330 V{py + ph}"/>')
    P.append(f'<path class="cv f-hypotheses-rej" d="M736,{py + ph} C736,560 712,560 712,{tray_y - 2}" marker-end="url(#arr)"/>')
    lane = f"M736,{py + ph} V660 Q736,676 720,676 H40 Q24,676 24,692 V774 Q24,790 40,790 H66"
    P.append(f'<path class="cv f-hypotheses-in" d="{lane}" marker-end="url(#arr)"/>')
    # tier 2: near-duplicates, tournament, rank
    ddx, ddy = 100, 790
    P.append(hdr(40, 728, "NEAR-DUPLICATES") + '<text class="sub" x="40" y="840">removed first</text>')
    x0, y0, c = 244, 766, 28
    P.append(hdr(200, 728, "TOURNAMENT · BLIND"))
    seat_xy = [(x0 - 36, y0 + i * c + c / 2) for i in range(N_SEAT)]
    G = {
        "nozzle": lambda g: (459, mids[g]),
        "enter": lambda g, n: [(F["x0"] + 6, mids[g] + ((n // N_GEN) - 1.5) * 4)],
        "check": lambda fate, n: ((540 + (n * 37) % 60, rows_y[fate[1]] - 4) if fate[0] == "hard"
                                  else (560 + (n * 29) % 70, 266 + ((n * 13) % 40 - 20) * .8)),
        "slot": lambda p: _cub(p, (p[0] + 40, p[1] + 10), (slot[0] - 20, slot[1] - 20), slot, 4),
        "chute": lambda: _cub(slot, (660, 420), (700, 500), (700, tray_y + 8), 6),
        "rest": lambda i: rest[i],
        "neck": lambda n: [(F["x1"] - 4, 266 + ((n % 5) - 2) * 4)],
        "lens_in": lambda spot: _hcurve((F["x1"] - 4, 266), spot, 5),
        "lens_spots": lambda m: _sun(lx, ly, 42, m),
        "lens_out": lambda spot: [(lx - 44, ly + 46)] + _cub((lx - 44, ly + 46), (750, 290), (736, 300), (736, 330), 3) + [(736, py + ph)],
        "tray2": lambda i: _cub((736, py + ph), (736, 560), (712, 560), (712, tray_y + 8), 4) + [rest[N_HARD + i]],
        "lane": lambda: [(736, 660), (720, 676), (40, 676), (24, 692), (24, 774), (40, 790), (66, 790)],
        "dedup": (ddx, ddy),
        "seat": lambda s: _hcurve((ddx + 24, ddy), seat_xy[s], 6),
    }
    parts, seat_t, dup_t = _particles(G)
    P.append(_dedup(ddx, ddy, dup_t) + _table(x0, y0, c, seat_t))
    P.append(f'<text class="lbl f-hypotheses-tn" x="{x0}" y="{y0 + N_SEAT * c + 24}">deep: similar pairs, ≤ 150 (default)</text>'
             f'<text class="lbl f-hypotheses-tn" x="{x0}" y="{y0 + N_SEAT * c + 42}">blank: not paired</text>')
    P.append(_game(482, 744, 168))
    P.append(f'<text class="lbl f-hypotheses-tn" x="482" y="944">the judge sees no IDs,</text>'
             f'<text class="lbl f-hypotheses-tn" x="482" y="962">generator or lineage</text>')
    # rank
    zx, sc, ry0, rp = 950, 36, 785, 28
    P.append(hdr(660, 728, "RANK"))
    P.append('<text class="tag" x="664" y="756">#</text><text class="tag" x="690" y="756">ID</text>'
             '<text class="tag" x="752" y="756" text-anchor="middle">CRITIC</text>'
             '<text class="tag" x="818" y="756" text-anchor="middle">SOFT</text>'
             f'<text class="tag" x="{zx}" y="756" text-anchor="middle">BRADLEY–TERRY STRENGTH</text>')
    P.append(_axis(zx, sc, 762, ry0 + (N_SEAT - 1) * rp + 10, ry0 + (N_SEAT - 1) * rp + 30))
    P.append(_bars(690, 752, 818, zx, sc, ry0, rp, seat_t) + _rank_nums(666, ry0, rp))
    P.append(f'<text class="lbl" x="660" y="{ry0 + (N_SEAT - 1) * rp + 52}">order: gate, critic score, flaws, soft checks, then strength</text>'
             f'<text class="lbl" x="660" y="{ry0 + (N_SEAT - 1) * rp + 70}">log strength · 95 % bootstrap interval, 200 resamples</text>')
    P.append(f'<g filter="url(#{pre}-glow)">{parts}</g>')
    P.append(legend(LEGEND, 30, H - 38) + note(30, H - 12))
    return svg(W, H, "".join(P), "wide", LABEL), seat_t


# ---------------------------------------------------------------- narrow
NARROW = {"W": 360}


def _narrow():
    W, pre = NARROW["W"], "hypotheses-n"
    P = [_defs(pre), hdr(16, 24, "RETRIEVE")]
    for k, (t, s) in enumerate(SOURCES):
        P.append(_src(24, 34 + 38 * k, 320, 32, t, s, True))
    P.append('<path class="cv f-hypotheses-in" d="M24,50 H12 M24,88 H12 M24,126 H12 M12,50 V170 H20" marker-end="url(#arr)"/>')
    P.append(_src(24, 154, 320, 32, "Inspirations", "model-screened", True))
    P.append(hdr(16, 218, "GENERATORS")
             + '<text class="lbl f-hypotheses-tier" x="344" y="218" text-anchor="end">tag: lowest effort that runs it</text>')
    tags = {"quick": "QUICK+", "standard adds": "STANDARD+", "deep adds": "DEEP"}
    gens = [(232 + 46 * k, tags[tier], *it) for k, (tier, it) in enumerate((t, it) for t, items in TIERS for it in items)]
    mids = [gy + 21 for gy, *_ in gens]
    P.append(_flow(f"M12,170 V{mids[-1]}", .05))
    P += [f'<path class="cv f-hypotheses-in" d="M12,{m} H22" marker-end="url(#arr)"/>' for m in mids]
    for g, (gy, tier, name, sub, db) in enumerate(gens):
        P.append(_gen(24, gy, 280, 42, name, sub, db, g, tier))
    gb = gens[-1][0] + 42  # generators' bottom
    # vertical funnel: mouth on top, neck below
    f0 = gb + 40
    P.append(hdr(16, f0 - 12, "SCREEN · HARD CHECKS"))
    fl, fr, nl, nr, fh = 16, 344, 150, 210, 240

    def edges(yy):
        t = (yy - f0) / fh
        return fl + t * (nl - fl), fr + t * (nr - fr)
    P.append(f'<path class="f-hypotheses-funnel" d="M{fl},{f0} L{fr},{f0} L{nr},{f0 + fh} L{nl},{f0 + fh} Z"/>'
             f'<path class="f-hypotheses-rim" d="M{fl},{f0} H{fr}"/>')
    rows = []
    for k, c in enumerate(CHECKS):
        yy = f0 + 22 + 22 * k
        wdt = 13 + len(c) * 8.04
        x = 180 - (wdt + 13) / 2 + 6.5
        le, re = edges(yy - 12)
        assert le + 2 < x - 7 and x + 13 + len(c) * 8.04 < re - 2, (c, le, re)
        P.append(_check(x, yy, c))
        rows.append((x, yy))
    slot = edges(f0 + 170)[0], f0 + 170
    t1 = (16, f0 + 186, 96, 98)  # tray 1: hard-check failures, beside the funnel's lower half
    assert t1[0] + t1[2] < edges(t1[1])[0] - 4
    P.append(f'<path class="cv f-hypotheses-rej" d="M{f(slot[0])},{f(slot[1])} C{f(slot[0] - 10)},{f(slot[1] + 10)} '
             f'{f(t1[0] + 76)},{f(t1[1] - 14)} {f(t1[0] + 76)},{f(t1[1] - 2)}" marker-end="url(#arr)"/>')
    P.append(_tray(*t1, t1[0] + 12, t1[1] + 20))
    rest1 = [(t1[0] + 16 + 16 * (i % 5), t1[1] + 40 + 18 * (i // 5)) for i in range(N_HARD)]
    assert rest1[-1][1] + 8 < t1[1] + t1[3]
    notes = ["no identifier", "→ unknown,", "never a failure"]
    for k, s in enumerate(notes):
        P.append(f'<text class="lbl f-hypotheses-fn" x="344" y="{f0 + 202 + 18 * k}" text-anchor="end">{escape(s)}</text>')
    assert edges(f0 + 202 - 12)[1] + 4 < 344 - max(map(len, notes)) * 6.8  # the notes clear the funnel's right edge
    # panel
    py = f0 + fh + 52
    ph = 412
    lx, ly, lr = 92, py + 104, 56
    P.append(f'<text class="lbl f-hypotheses-fn" x="344" y="{f0 + fh + 26}" text-anchor="end">soft checks only</text>'
             f'<text class="lbl f-hypotheses-fn" x="344" y="{f0 + fh + 44}" text-anchor="end">lower the rank</text>')
    P.append(f'<path class="cv f-hypotheses-in" d="M180,{f0 + fh} C180,{py - 16} {lx + 20},{py + 8} {lx + 20},{ly - lr - 4}" marker-end="url(#arr)"/>')
    P.append('<g class="f-hypotheses-lm">' + _panel_head(pre, 16, py, 328, ph, 176, py + 34, ["reviews against", "≤ 8 passages"]))
    P.append(_lens(pre, lx, ly, lr, (lx + 40, ly + 40, lx + 56, ly + 56)))
    P.append(_verdicts(178, py + 86, 160, 26))
    for k, s in enumerate(["“supports”/“disproved” need a verbatim quote,", "else neutral; a quoted “disproved” rejects"]):
        P.append(f'<text class="lbl f-hypotheses-pl" x="30" y="{py + 262 + 19 * k}">{escape(s)}</text>')
    P.append(_critic(30, py + 322, 80, 8))
    P.append(f'<text class="sub f-hypotheses-on" x="{30 + 3 * 88}" y="{py + 351.5}">→ 1–5</text>'
             f'<text class="lbl f-hypotheses-pl" x="30" y="{py + 384}">a fatal flaw rejects, unless</text>'
             f'<text class="lbl f-hypotheses-pl" x="30" y="{py + 402}">none would remain</text></g>')
    pb = py + ph
    out_pts = [(lx - 42, ly + 36), (22, ly + 70), (22, pb)]
    P.append(f'<path class="cv f-hypotheses-in" d="M{lx - 42},{ly + 36} C28,{ly + 48} 22,{ly + 58} 22,{ly + 78} V{pb}"/>')
    # review rejects branch right under the panel into tray 2; the lane carries on down to the near-duplicates
    t2 = (238, pb + 24, 106, 56)
    br = pb + 46
    rest2 = [(t2[0] + 22 + 20 * i, t2[1] + 40) for i in range(N_REV)]
    P.append(f'<path class="cv f-hypotheses-rej" d="M22,{pb} V{br - 10} Q22,{br} 32,{br} H{t2[0] - 2}" marker-end="url(#arr)"/>')
    P.append(_tray(*t2, t2[0] + 12, t2[1] + 20))
    ddx, ddy = 72, pb + 92
    P.append(f'<path class="cv f-hypotheses-in" d="M22,{pb} V{ddy - 14} Q22,{ddy} 36,{ddy}"/>')
    P.append(hdr(46, pb + 30, "NEAR-DUPLICATES") + f'<text class="sub" x="{ddx + 46}" y="{ddy + 5}">removed first</text>')
    # tournament
    ty0 = ddy + 58
    x0, c = 76, 30
    y0 = ty0 + 30
    P.append(hdr(100, ty0, "TOURNAMENT · BLIND"))
    seat_xy = [(x0 - 36, y0 + i * c + c / 2) for i in range(N_SEAT)]
    P.append(f'<path class="cv f-hypotheses-in" d="M{ddx},{ddy + 20} C{ddx},{ddy + 44} {x0 - 60},{y0 - 20} {x0 - 46},{y0 + 4}" marker-end="url(#arr)"/>')
    G = {
        "nozzle": lambda g: (315, mids[g]),
        "enter": lambda g, n: _vcurve((315, mids[g]), (330 - ((n * 7) % 9), f0 + 6), 4),
        "check": lambda fate, n: ((rows[fate[1]][0] + 40 + (n * 11) % 30, rows[fate[1]][1] - 4) if fate[0] == "hard"
                                  else (180 + ((n * 37) % 80 - 40) * (.9 - .4 * ((n % 3) / 2)), f0 + 100 + (n * 23) % 70)),
        "slot": lambda p: _cub(p, (p[0] - 20, p[1] + 10), (slot[0] + 20, slot[1] - 10), slot, 4),
        "chute": lambda: _cub(slot, (slot[0] - 10, slot[1] + 10), (t1[0] + 76, t1[1] - 14), (t1[0] + 76, t1[1] + 8), 4),
        "rest": lambda i: rest1[i],
        "neck": lambda n: [(176 + (n % 5) * 2, f0 + fh - 4)],
        "lens_in": lambda spot: _cub((180, f0 + fh), (180, py - 16), (lx + 20, py + 8), spot, 6),
        "lens_spots": lambda m: _sun(lx, ly, 38, m),
        "lens_out": lambda spot: [out_pts[0]] + _cub(out_pts[0], (28, ly + 48), (22, ly + 58), (22, ly + 78), 3) + [(22, pb)],
        "tray2": lambda i: [(22, br - 10), (32, br), (t2[0] + 8, br), rest2[i]],
        "lane": lambda: [(22, ddy - 14), (36, ddy)],
        "dedup": (ddx, ddy),
        "seat": lambda s: _cub((ddx, ddy + 20), (ddx, ddy + 44), (x0 - 60, y0 - 20), seat_xy[s], 6),
    }
    parts, seat_t, dup_t = _particles(G)
    P.append(_dedup(ddx, ddy, dup_t) + _table(x0, y0, c, seat_t))
    tb = y0 + N_SEAT * c
    P.append(f'<text class="lbl f-hypotheses-tn" x="16" y="{tb + 24}">deep: similar pairs, ≤ 150 (default)</text>'
             f'<text class="lbl f-hypotheses-tn" x="16" y="{tb + 43}">blank: not paired</text>')
    gy = tb + 58
    P.append(_game(16, gy, 328, side=True))
    P.append(f'<text class="lbl f-hypotheses-tn" x="16" y="{gy + 126}">the judge sees no IDs, generator or lineage</text>')
    # rank: columns as in the wide variant
    ry = gy + 168
    zx, sc, ry0, rp = 250, 31, ry + 50, 28
    P.append(hdr(16, ry, "RANK")
             + f'<text class="tag" x="16" y="{ry + 26}">#</text><text class="tag" x="32" y="{ry + 26}">ID</text>'
             f'<text class="tag" x="86" y="{ry + 26}" text-anchor="middle">CRITIC</text>'
             f'<text class="tag" x="140" y="{ry + 26}" text-anchor="middle">SOFT</text>'
             f'<text class="tag" x="{zx}" y="{ry + 26}" text-anchor="middle">LOG STRENGTH</text>')
    P.append(_axis(zx, sc, ry0 - 18, ry0 + (N_SEAT - 1) * rp + 10, ry0 + (N_SEAT - 1) * rp + 30))
    P.append(_bars(32, 86, 140, zx, sc, ry0, rp, seat_t) + _rank_nums(16, ry0, rp))
    ly2 = ry0 + (N_SEAT - 1) * rp + 54
    for k, s in enumerate(["order: gate, critic score, flaws, soft checks,", "then strength",
                           "95 % bootstrap interval, 200 resamples"]):
        P.append(f'<text class="lbl" x="16" y="{ly2 + 19 * k}">{escape(s)}</text>')
    H = ly2 + 68 + 26 * 3 + 10
    rows_lg = [LEGEND[:2], LEGEND[2:3], [("dash", "failed: excluded")]]
    P.append(f'<g filter="url(#{pre}-glow)">{parts}</g>')
    P.append("".join(legend(r, 16, ly2 + 68 + 26 * k) for k, r in enumerate(rows_lg)) + note(16, H - 8))
    return svg(W, H, "".join(P), "narrow", LABEL), seat_t


JS = """MAFig.register("hypotheses", function (root, variant) {
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var at = function (el) { return +el.getAttribute("data-t"); };
  var parts = q(".f-hypotheses-pt"), flash = q(".f-hypotheses-fl"), glow = q(".f-hypotheses-nglow"),
    rows = q(".f-hypotheses-row"), bars = q(".f-hypotheses-bar"), scan = root.querySelector(".f-hypotheses-scan"),
    gc = q(".f-hypotheses-gc"), goes = q(".f-hypotheses-go");
  // shown in the finished frame, hidden until the step that decides them
  var shown = q(".f-hypotheses-frame, .f-hypotheses-out, .f-hypotheses-ci, .f-hypotheses-rk, .f-hypotheses-qh");
  gsap.set(bars, {svgOrigin: function (i, el) { return el.getAttribute("data-z") + " 0"; }});
  var pulse = function (tl, el, t, d) {
    tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: .1}, t).to(el, {opacity: 0, duration: d || .45}, t + (d ? .1 : .3));
  };
  // one pass of the machine from time t0. Every key in a fromTo start object is repeated in its end object (a loop
  // wrap drops start-only keys).
  function pass(tl, t0) {
    q(".f-hypotheses-flow").forEach(function (el) {
      tl.fromTo(el, {drawSVG: "0% 0%", opacity: 1}, {drawSVG: "0% 100%", opacity: 1, duration: .4, ease: "power1.in"}, t0 + at(el))
        .to(el, {opacity: 0, duration: .25}, t0 + at(el) + .45);
    });
    parts.forEach(function (p) {
      var w = p.getAttribute("data-p").split(" ").map(function (s) { return s.split(":").map(Number); });
      var c = p.querySelector(".f-hypotheses-ptc"), a = p.querySelector(".f-hypotheses-pta");
      var ta = p.getAttribute("data-a"), to = p.getAttribute("data-o"), r = p.getAttribute("data-r");
      tl.fromTo(p, {x: w[0][1], y: w[0][2], opacity: 0}, {x: w[0][1], y: w[0][2], opacity: 1, duration: .12}, t0 + w[0][0])
        .fromTo(c, {opacity: 1}, {opacity: 1, duration: .01}, t0 + w[0][0])
        .fromTo(a, {opacity: 0}, {opacity: 0, duration: .01}, t0 + w[0][0]);
      pulse(tl, glow[+p.getAttribute("data-g")], t0 + w[0][0] - .05, .15);
      for (var i = 1; i < w.length; i++) {
        tl.to(p, {x: w[i][1], y: w[i][2], duration: w[i][0] - w[i - 1][0], ease: i === w.length - 1 ? "power2.out" : "none"}, t0 + w[i - 1][0]);
      }
      if (ta) {
        tl.fromTo(a, {opacity: 0}, {opacity: 1, duration: .15}, t0 + +ta).fromTo(c, {opacity: 1}, {opacity: 0, duration: .15}, t0 + +ta);
        if (r !== null) pulse(tl, flash[+r], t0 + +ta, .2);
      }
      if (to) tl.to(p, {opacity: 0, duration: .3}, t0 + +to);
    });
    // the lens scans, the verdicts and the critic's flaws light as they are given
    tl.fromTo(scan, {y: 0, opacity: 0}, {y: 0, opacity: 1, duration: .2}, t0 + at(scan))
      .to(scan, {y: +scan.getAttribute("data-dy"), duration: __SCAN__, ease: "sine.inOut"}, t0 + at(scan))
      .to(scan, {opacity: 0, duration: .2}, t0 + at(scan) + __SCAN__);
    q(".f-hypotheses-vp, .f-hypotheses-cs, .f-hypotheses-sockp, .f-hypotheses-ddp").forEach(function (el) { pulse(tl, el, t0 + at(el)); });
    shown.forEach(function (el) { tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: .25}, t0 + at(el)); });
    q(".f-hypotheses-swap").forEach(function (el) { pulse(tl, el, t0 + at(el) - .3); });
    // one game: the two candidates swap slots between the judge's two calls
    goes.forEach(function (el) { tl.fromTo(el, {opacity: .35}, {opacity: 1, duration: .3}, t0 + at(el)); });
    gc.forEach(function (el) {
      tl.fromTo(el, {x: 0}, {x: +el.getAttribute("data-dx"), duration: .4, ease: "power2.inOut"}, t0 + __SWAP__)
        .to(el, {x: 0, duration: .4, ease: "power2.inOut"}, t0 + __BACK__);
    });
    // leaderboard: rows appear in seat order, bars grow, then the rows settle into the final order
    rows.forEach(function (el) {
      var dy = +el.getAttribute("data-dy");
      tl.fromTo(el, {y: dy, opacity: 0}, {y: dy, opacity: 1, duration: .3}, t0 + at(el))
        .fromTo(el, {y: dy}, {y: 0, duration: .6, ease: "power2.inOut"}, t0 + __SORT__);
    });
    bars.forEach(function (el) { tl.fromTo(el, {scaleX: 0}, {scaleX: 1, duration: .6, ease: "power3.out"}, t0 + at(el)); });
  }
  var intro = gsap.timeline({defaults: {ease: "power3.out"}});
  intro.from(q(".hdr, .f-hypotheses-tier"), {opacity: 0, duration: .5}, 0)
    .from(q(".f-hypotheses-src"), {opacity: 0, x: -10, duration: .35, stagger: .06}, .1)
    .from(q(".f-hypotheses-gen"), {opacity: 0, x: -12, duration: .35, stagger: .05}, .2)
    .from(q(".f-hypotheses-in"), {drawSVG: 0, duration: .6, stagger: .02}, .3)
    .from(q(".f-hypotheses-rej"), {opacity: 0, duration: .5}, .6)
    .from(q(".f-hypotheses-funnel, .f-hypotheses-rim, .f-hypotheses-tray, .f-hypotheses-eff"), {opacity: 0, duration: .5}, .3)
    .from(q(".f-hypotheses-chk"), {opacity: 0, x: -6, duration: .25, stagger: .04}, .4)
    .from(q(".f-hypotheses-lm"), {opacity: 0, scale: .97, transformOrigin: "50% 50%", duration: .5}, .5)
    .from(q(".f-hypotheses-fn, .f-hypotheses-tn, .f-hypotheses-dd, .f-hypotheses-seat, .f-hypotheses-game"), {opacity: 0, duration: .4}, .6)
    .from(q(".f-hypotheses-cell, .f-hypotheses-diag, .f-hypotheses-hid"), {opacity: 0, duration: .3, stagger: .004}, .7)
    .from(q(".f-hypotheses-zero, .f-hypotheses-tick, .tag, .lbl:not(.f-hypotheses-tier):not(.f-hypotheses-fn):not(.f-hypotheses-tn)"), {opacity: 0, duration: .4}, .8)
    .from(q(".legend"), {opacity: 0, duration: .4}, 1.0);
  pass(intro, __T0I__);
  // loop: hold the finished frame, clear the results and the particles, replay the pass. immediateRender off: the
  // finished frame stays until the clear.
  var loop = gsap.timeline({repeat: -1, defaults: {immediateRender: false}});
  loop.to(parts, {opacity: 0, duration: .5}, __HOLD__)
    .to(shown, {opacity: 0, duration: .5}, __HOLD__)
    .to(rows, {opacity: 0, duration: .5}, __HOLD__)
    .to(bars, {scaleX: 0, duration: .5}, __HOLD__)
    .to(goes, {opacity: .35, duration: .5}, __HOLD__);
  pass(loop, __T0L__);
  loop.set({}, {}, __TL__);
  return {intro: intro, loop: loop};
});"""
JS = (JS.replace("__SCAN__", str(SCAN)).replace("__SWAP__", str(GAME_T["swap"])).replace("__BACK__", str(GAME_T["back"])).replace("__SORT__", str(SORT_T))
      .replace("__T0I__", str(T0_INTRO)).replace("__T0L__", str(round(T0_LOOP, 3))).replace("__HOLD__", str(HOLD))
      .replace("__TL__", str(T_LOOP)))


def build():
    wide, st_w = _wide()
    narrow, st_n = _narrow()
    assert st_w == st_n, (st_w, st_n)  # both variants run on one clock
    return Figure(wide=wide, narrow=narrow, js=JS)
