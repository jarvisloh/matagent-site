"""VASP figure: a three-panel engine for VW 9.1-9.7 (claims C22, C23, C60-C65; all running behaviour assumed).
(a) Structure bench: a Cu(111) slab, cut from bulk with 15 A of vacuum, gets CO placed on an ontop site; INCAR,
POSCAR, KPOINTS and POTCAR fan out (POTCAR is assembled on the cluster and never leaves it). (b) Governed queue: one
approval per run (amber) holds a gate shut; once approved its bars retract and the run's three jobs go through the
cluster's Slurm lanes in order, PENDING -> RUNNING -> COMPLETED; the cluster is the one dark panel. (c) Results,
fetched and parsed: the adsorption energy, NEB images sliding along the energy path to a climbing image, EOS points
and a Birch-Murnaghan fit that bends into shape, and a DOS trace. Wide is scrubbed (a -> b -> c, top to bottom, so
each element finishes on screen); narrow plays once. The SVG is the finished frame. A result appears only after the
step that decides it: tokens enter only after the approval, ticks after RUNNING, values after their fits."""
import math
from html import escape

from figkit import Figure, curve_d, f, hdr, legend, note, svg

NB = "\u202f"  # narrow no-break space before units
CW = {"wide": 7.68, "narrow": 8.04}  # Geist Mono advance per character at the sub size
TAGW = {"wide": 9.22, "narrow": 9.65}  # tag advance (0.6 em + .12 em letter-spacing)

# --- the example structure: CO atop Cu(111), drawn to scale in a side view along [1-10] (illustrative) -------------
S = 11.0  # viewBox units per angstrom
A_NN = 2.55  # Cu nearest-neighbour distance (A)
DX = A_NN * math.sqrt(3) / 2 * S  # projected in-plane spacing of atom rows
DZ = 2.08 * S  # Cu(111) interlayer spacing
NCOL, NLAY = 8, 5  # columns per cell; 5 layers (pymatgen: ceil(10 A / 2.08 A))
CELL_W = NCOL * DX
R_CU, R_C, R_O = 10.0, 5.5, 6.0
D_CUC, D_CO = 1.85 * S, 1.15 * S  # Cu-C and C-O bond lengths
SITE = 3  # the ontop atom (top layer column)

# --- results (illustrative): one run's E_ads; NEB; EOS and DOS of fcc Cu ---------------------------------------
E_ADS = "−0.71"
NEB_E = [0.0, 0.10, 0.40, 0.62, 0.40, 0.05, -0.25]  # eV: IS, five images, FS; image 3 is the climbing image
CI = NEB_E.index(max(NEB_E))
assert CI == 3 and NEB_E[CI - 1] == NEB_E[CI + 1]  # symmetric neighbours: the path's maximum sits on the CI
V0, B0_GPA, BP, E0 = 12.0, 140.0, 5.0, -3.73  # A^3/atom, GPa, -, eV/atom
EOS_V = [11.1 + 0.3 * k for k in range(7)]
EOS_NOISE = [0.3, -0.4, 0.2, -0.2, 0.3, -0.3, 0.2]  # meV scatter about the fit


def bm(v):
    """Third-order Birch-Murnaghan E(V) - E0 in eV/atom."""
    b0 = B0_GPA / 160.21766  # GPa -> eV/A^3
    x = (V0 / v) ** (2 / 3) - 1
    return 9 * V0 * b0 / 16 * (x ** 3 * BP + x ** 2 * (6 - 4 * (V0 / v) ** (2 / 3)))


EOS_PTS = [(v, bm(v) * 1000 + n) for v, n in zip(EOS_V, EOS_NOISE)]  # meV
assert min(range(7), key=lambda k: EOS_PTS[k][1]) == 3 and bm(11.1) > bm(12.9) > 0  # convex, min at V0, BM asymmetry


def dos(e):
    """Illustrative total DOS of Cu (states/eV): an sp background and the d band between about -5.3 and -1.5 eV."""
    sp = 0.32 * math.sqrt(max(e + 9.6, 0) / 9.6)
    d = sum(h * math.exp(-((e - c) / w) ** 2) for c, h, w in
            ((-4.7, .55, .32), (-3.75, 1.75, .34), (-3.05, 1.25, .28), (-2.35, 2.55, .27), (-1.8, 1.5, .2)))
    return sp + d


assert dos(0) < 0.5 and dos(-2.35) > 2.4  # metallic: low DOS at the Fermi level, no gap

# --- the scrub schedule (s); one clock for both variants. Wide maps 0..T_END onto the scroll range ---------------
T = {"head": 0, "ahead": .3, "vac": 1.1, "dim": 2.6, "layer0": 2.75, "co": 4.85, "fan": 5.3, "file0": 5.35,
     "bhead": 5.8, "appr": 5.85, "cluster": 5.95, "conn": 6.05, "press": 6.4, "ok2gate": 6.55, "gate": 6.65,
     "gok": 7.0, "flow": 7.05, "tok0": 7.15, "fail": 9.95, "cue": 10.0, "ads": 10.05, "neb": 10.1, "eos": 10.2,
     "dos": 10.3}
TOK_PITCH, LAYER_PITCH, FILE_PITCH = .95, .42, .12
# a job's beats, from entering PENDING: RUNNING (two pulse sweeps), COMPLETED, tick, then its folder is fetched
# and parsed (a dot runs down to the parser chips)
TOK = {"run": .12, "pulse": .26, "done": .5, "tick": .62, "fetch": .74, "end": .9}
# steps are submitted in order: the next job enters PENDING only after the previous one is COMPLETED and its
# outputs fetched and parsed (C62)
assert TOK_PITCH >= .75 and round(TOK_PITCH - TOK["end"], 6) >= .05
T["parse"] = T["chip0"] = T["chead"] = T["tok0"] + TOK["fetch"] - .1  # results row opens with the first fetch
assert round(T["tok0"] + 2 * TOK_PITCH + TOK["end"], 6) <= T["fail"] <= T["ads"]
T_END = 12.0


class Rec:
    """Wide only: each timed element's (end time, top y, bottom y), to check it finishes on screen during the scrub."""
    def __init__(self):
        self.items = []

    def __call__(self, t, d, y0, y1):
        self.items.append((t + d, y0, y1))


def _tv(t):
    return f"{t:.2f}".rstrip("0").rstrip(".")


def rv(body, t, rec, y0, y1, d=.3, dx=0, dy=0, cls=""):
    """Generic reveal group: fades in (and slides by dx, dy) at time t."""
    rec(t, d, y0, y1)
    extra = (f' data-dx="{dx}"' if dx else "") + (f' data-dy="{dy}"' if dy else "") + (f' data-d="{_tv(d)}"' if d != .3 else "")
    c = f"f-vasp-rv {cls}".strip()
    return f'<g class="{c}" data-t="{_tv(t)}"{extra}>{body}</g>'


def dr(d_attr, t, rec, y0, y1, cls, dur=.3, arrow=False):
    """A path drawn on (DrawSVG) at time t; solid strokes only (the plugin overrides dash patterns)."""
    rec(t, dur, y0, y1)
    m = ' marker-end="url(#arr)"' if arrow else ""
    return f'<path class="{cls} f-vasp-dr" d="{d_attr}" data-t="{_tv(t)}" data-d="{_tv(dur)}"{m}/>'


def badge(x, y, letter, title):
    return (f'<circle class="f-vasp-badge" cx="{f(x + 10)}" cy="{f(y - 4.5)}" r="10"/>'
            f'<text class="f-vasp-bt" x="{f(x + 10)}" y="{f(y)}" text-anchor="middle">{letter}</text>' + hdr(x + 28, y, title))


def _defs(pre):
    return (f'<defs><linearGradient id="{pre}-pnl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="f-vasp-g0"/>'
            '<stop offset="1" class="f-vasp-g1"/></linearGradient></defs>')


# ------------------------------------------------------------------------------------------------- (a) bench ----
def slab(pre, X, CT, TL, rec, wide):
    """Periodic cell (dashed, clipped) with five Cu(111) layers, CO atop, vacuum dimension and break marks.
    X: cell left; CT: cell top; TL: top-layer atom centre y. Returns markup and the cell's bottom y."""
    cb = TL + (NLAY - 1) * DZ + DZ / 2
    cid = f"{pre}-cell"
    P = [f'<clipPath id="{cid}"><rect x="{f(X)}" y="{f(CT)}" width="{f(CELL_W)}" height="{f(cb - CT)}"/></clipPath>']
    # vacuum texts, then the dimension: the vacuum above the top layer is not to scale (break marks)
    tx = X + 14
    vt = (f'<text class="ttl{"" if wide else " sm"}" x="{f(tx)}" y="{f(CT + 28)}">Cu(111) + CO</text>'
          f'<text class="sub" x="{f(tx)}" y="{f(CT + 50)}">slab: bulk + (111)</text>'
          f'<text class="sub" x="{f(tx)}" y="{f(CT + 70)}">CO on an ontop site</text>')
    P.append(rv(vt, T["vac"], rec, CT + 14, CT + 74))
    dimx = X - 12
    by = (CT + TL) / 2 + 28
    dim = (f'<path class="f-vasp-dim" d="M{f(dimx)},{f(CT + 2)} V{f(TL - 2)}" marker-start="url(#arr)" marker-end="url(#arr)"/>'
           f'<text class="sub" x="{f(dimx - 8)}" y="{f((CT + TL) / 2)}" text-anchor="middle" '
           f'transform="rotate(-90 {f(dimx - 8)} {f((CT + TL) / 2)})">vacuum 15{NB}Å</text>')
    P.append(rv(dim, T["dim"], rec, CT, TL))
    lay_t = [T["layer0"] + LAYER_PITCH * l for l in range(NLAY)]
    for l in range(NLAY):
        y = TL + l * DZ
        off = (l % 3) * DX / 3
        atoms = "".join(f'<circle class="f-vasp-cu{" top" if l == 0 else ""}" cx="{f(X + (j + .5) * DX + off)}" cy="{f(y)}" r="{R_CU}"/>'
                        for j in range(-1, NCOL + 1))  # one image column each side, clipped to the cell
        P.append(rv(f'<g clip-path="url(#{cid})">{atoms}</g>', lay_t[l], rec, y - R_CU, y + R_CU, dy=-6))
    cell = (f'<rect class="f-vasp-cell" x="{f(X)}" y="{f(CT)}" width="{f(CELL_W)}" height="{f(cb - CT)}"/>'
            + "".join(f'<path class="f-vasp-brk" d="M{f(x - 6)},{f(by + 3)} l12,-8 M{f(x - 6)},{f(by + 9)} l12,-8"/>'
                      for x in (X, X + CELL_W)))
    P.append(rv(cell, lay_t[-1], rec, CT, cb))
    # CO placed atop SITE: C down, at the Cu-C bond length above the surface atom
    sx = X + (SITE + .5) * DX
    cy_, oy = TL - D_CUC, TL - D_CUC - D_CO
    co = (f'<path class="f-vasp-bond" d="M{f(sx)},{f(TL - R_CU + 1)} V{f(cy_ + R_C - 1)}"/>'
          f'<path class="f-vasp-bond dbl" d="M{f(sx - 2)},{f(cy_)} V{f(oy)} M{f(sx + 2)},{f(cy_)} V{f(oy)}"/>'
          f'<circle class="f-vasp-c" cx="{f(sx)}" cy="{f(cy_)}" r="{R_C}"/><circle class="f-vasp-o" cx="{f(sx)}" cy="{f(oy)}" r="{R_O}"/>'
          f'<text class="sub" x="{f(sx - 11)}" y="{f(cy_ + 4.5)}" text-anchor="end">C</text>'
          f'<text class="sub" x="{f(sx + 11)}" y="{f(oy + 4.5)}">O</text>')
    P.append(rv(co, T["co"], rec, oy - R_O, TL, d=.4, dy=-40, cls="f-vasp-co"))
    return "".join(P), cb


FILES = [  # name, sub-label (<= 22), right tag
    ("INCAR", "ENCUT 1.3 × max ENMAX", "PRESET"),
    ("POSCAR", "slab + CO positions", ""),
    ("KPOINTS", "Γ-centred mesh", ""),
]


def file_card(x, y, w, h, k, rec, wide):
    name, sub, tag = FILES[k]
    assert 14 + len(sub) * CW["wide" if wide else "narrow"] + 12 <= w, sub
    ic = (f'<path class="f-vasp-page" d="M{f(x + 14)},{f(y + 10)} h9 l5,5 v13 h-14 z M{f(x + 23)},{f(y + 10)} v5 h5"/>')
    t = f'<text class="tag" x="{f(x + w - 14)}" y="{f(y + 23)}" text-anchor="end">{tag}</text>' if tag else ""
    body = (f'<g class="card f-vasp-file"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="9"/>'
            f'{ic}<text class="ttl sm" x="{f(x + 38)}" y="{f(y + 24)}">{name}</text>{t}'
            f'<text class="sub" x="{f(x + 14)}" y="{f(y + h - 12)}">{escape(sub)}</text></g>')
    return rv(body, T["file0"] + FILE_PITCH * k, rec, y, y + h, dx=-14)


# ------------------------------------------------------------------------------------------------- (b) queue ----
APPR = ["planned steps", "first step's inputs", "Slurm profile", "core-hour ceiling"]


def approval(x, y, w, h, rec, wide):
    """The amber approval card: what the approval shows, and Approve / Reject (Approve is pressed: its tick)."""
    P = [f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>',
         f'<text class="tag f-vasp-amb" x="{f(x + 16)}" y="{f(y + 22)}">APPROVAL · ONE PER RUN</text>',
         f'<text class="ttl{"" if wide else " sm"}" x="{f(x + 16)}" y="{f(y + 46)}">Approve this run?</text>',
         f'<text class="lbl" x="{f(x + 16)}" y="{f(y + 66)}">in chat or the Approval Inbox</text>',
         f'<text class="lbl amb" x="{f(x + 16)}" y="{f(y + (88 if wide else h - 12))}">off-plan step: asks again</text>']
    lx, ly = (x + 228, y + 24) if wide else (x + 16, y + 94)
    for k, s in enumerate(APPR):
        P.append(f'<circle class="f-vasp-li" cx="{f(lx + 3)}" cy="{f(ly + 18 * k - 4)}" r="2.5"/>'
                 f'<text class="sub" x="{f(lx + 12)}" y="{f(ly + 18 * k)}">{escape(s)}</text>')
    bw, bh = 92, 26
    bx = x + w - 16 - bw
    b1, b2 = (y + 16, y + 52) if wide else (y + 84, y + 118)
    P.append(f'<g class="f-vasp-btn ok"><rect x="{f(bx)}" y="{f(b1)}" width="{bw}" height="{bh}" rx="7"/>'
             f'<text class="sub" x="{f(bx + 30)}" y="{f(b1 + 17.5)}">Approve</text></g>'
             f'<use class="f-vasp-okb" href="#chk" x="{f(bx + 10)}" y="{f(b1 + 7)}" width="12" height="12" data-t="{_tv(T["press"])}"/>'
             f'<g class="f-vasp-btn no"><rect x="{f(bx)}" y="{f(b2)}" width="{bw}" height="{bh}" rx="7"/>'
             f'<text class="sub" x="{f(bx + bw / 2)}" y="{f(b2 + 17.5)}" text-anchor="middle">Reject</text></g>')
    rec(T["press"], .2, b1, b1 + bh)
    return rv(f'<g class="card f-vasp-appr">{"".join(P)}</g>', T["appr"], rec, y, y + h)


def gate(pre, x, y, w, h, vertical, rec):
    """Portcullis across the job path, held shut by the approval. vertical: bars hang across a horizontal path and
    retract up into the housing; else the grille lies across a vertical path and slides left into the housing.
    The static frame is open (bars retracted); the intro starts it shut."""
    cid = f"{pre}-gate"
    if vertical:  # housing on top: x..x+w, y..y+10; bars below
        hx, hy, hw, hh = x, y, w, 10
        clip = (x - 2, y + 10, w + 4, h - 10)
        bars = "".join(f'<path d="M{f(x + 4 + k * (w - 8) / 3)},{f(y + 10)} V{f(y + h - 4)}"/>' for k in range(4))
        bars += "".join(f'<path d="M{f(x + 2)},{f(y + 10 + (h - 14) * j / 3)} h{f(w - 4)}"/>' for j in (1, 2))
        dx, dy = 0, h
    else:  # housing on the left: x..x+10, y..y+h; grille to the right
        hx, hy, hw, hh = x, y, 10, h
        clip = (x + 10, y - 2, w - 10, h + 4)
        n = 14
        bars = "".join(f'<path d="M{f(x + 10 + (k + .5) * (w - 14) / n)},{f(y + 2)} V{f(y + h - 2)}"/>' for k in range(n))
        bars += "".join(f'<path d="M{f(x + 10)},{f(y + h * j / 3)} H{f(x + w - 4)}"/>' for j in (1, 2))
        dx, dy = w, 0
    cx, cy = hx - 12, hy + (5 if vertical else hh / 2)  # the approved tick, beside the housing
    rec(T["gate"], .35, y, y + h)
    rec(T["gok"], .3, cy - 8, cy + 8)
    return (f'<clipPath id="{cid}"><rect x="{f(clip[0])}" y="{f(clip[1])}" width="{f(clip[2])}" height="{f(clip[3])}"/></clipPath>'
            f'<g class="f-vasp-gate"><rect class="f-vasp-house" x="{f(hx)}" y="{f(hy)}" width="{f(hw)}" height="{f(hh)}" rx="2"/>'
            f'<g clip-path="url(#{cid})"><g transform="translate({f(-dx)},{f(-dy)})">'
            f'<g class="f-vasp-bars" data-t="{_tv(T["gate"])}" data-dx="{f(dx)}" data-dy="{f(dy)}">{bars}</g></g></g></g>'
            + rv(f'<circle class="f-vasp-gokc" cx="{f(cx)}" cy="{f(cy)}" r="8"/>'
                 f'<use class="f-vasp-gok" href="#chk" x="{f(cx - 6)}" y="{f(cy - 6)}" width="12" height="12"/>',
                 T["gok"], lambda *a: None, 0, 0))


LANES = ["PENDING", "RUNNING", "COMPLETED"]
JOBS = ["slab", "slab+CO", "CO (g)"]  # VW 9.4's three calculations, submitted in this order
RAN = ["ran 1.6 h", "ran 2.3 h", "ran 0.2 h"]  # sacct elapsed, illustrative


def token(x, y, w, k, p_off, r_off, rec, ybounds):
    """One Slurm job: enters PENDING (offset p_off), moves to RUNNING (r_off; an indeterminate pulse, no progress
    implied), ends COMPLETED."""
    t = T["tok0"] + TOK_PITCH * k
    rec(t, TOK["tick"] + .12, *ybounds)
    return (f'<g class="f-vasp-tok" data-t="{_tv(t)}" data-p="{f(p_off[0])} {f(p_off[1])}" data-r="{f(r_off[0])} {f(r_off[1])}">'
            f'<rect class="f-vasp-tr" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="26" rx="6"/>'
            f'<text class="sub f-vasp-pi" x="{f(x + 10)}" y="{f(y + 17.5)}">{escape(JOBS[k])}</text>'
            f'<rect class="f-vasp-run" x="{f(x + 4)}" y="{f(y + 21)}" width="28" height="3" rx="1.5" opacity="0" '
            f'data-tr="{f(w - 36)}"/>'
            f'<g class="f-vasp-tick"><circle cx="{f(x + w - 13)}" cy="{f(y + 13)}" r="8"/>'
            f'<path d="M{f(x + w - 17)},{f(y + 13.5)} l3,3 l5.5,-6.5"/></g></g>')


def ghosts(k, pend, run, w, rec):
    """The trail a job leaves once it moves on: a faint outline at its PENDING place (x, y), its elapsed time at its
    RUNNING place."""
    t = T["tok0"] + TOK_PITCH * k
    g = lambda x, y, s: (f'<rect class="f-vasp-gh" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="26" rx="6"/>'
                         f'<text class="sub f-vasp-pm" x="{f(x + 10)}" y="{f(y + 17.5)}">{escape(s)}</text>')
    return (rv(g(*pend, JOBS[k]), t + TOK["run"] + .12, rec, pend[1], pend[1] + 26, d=.15)
            + rv(g(*run, RAN[k]), t + TOK["done"] + .12, rec, run[1], run[1] + 26, d=.15))


def potcar(x, y, rec):
    """POTCAR, assembled on the cluster with the first job's script; it never leaves the cluster (dashed)."""
    return rv(f'<g class="f-vasp-pot"><rect x="{f(x)}" y="{f(y)}" width="88" height="22" rx="6"/>'
              f'<path class="f-vasp-page pk" d="M{f(x + 9)},{f(y + 4)} h7 l4,4 v10 h-11 z"/>'
              f'<text class="sub f-vasp-pi" x="{f(x + 28)}" y="{f(y + 15.5)}">POTCAR</text></g>', T["tok0"], rec, y, y + 22)


def cluster(pre, x, y, w, h, wide, rec):
    """The HPC cluster, the figure's one dark panel, with three Slurm lanes and the run's three jobs (final: done)."""
    P = [f'<rect class="panel" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="14" style="fill:url(#{pre}-pnl)"/>',
         f'<text class="tag f-vasp-pt" x="{f(x + 16)}" y="{f(y + 24)}">HPC CLUSTER · SLURM</text>']
    if wide:
        P.append(f'<text class="sub f-vasp-pm" x="{f(x + w - 16)}" y="{f(y + 24)}" text-anchor="end">sbatch over SSH</text>')
        lx0, gap = x + 12, 8
        lw = (w - 24 - 2 * gap) / 3
        top, bot = y + 52, y + h - 10
        for i, name in enumerate(LANES):
            lx = lx0 + i * (lw + gap)
            assert len(name) * TAGW["wide"] + 20 <= lw
            P.append(f'<rect class="f-vasp-lane" x="{f(lx)}" y="{f(top)}" width="{f(lw)}" height="{f(bot - top)}" rx="8"/>'
                     f'<text class="tag f-vasp-pk" x="{f(lx + 10)}" y="{f(top - 8)}">{name}</text>')
        tw = lw - 16
        P.append(potcar(x + 214, y + 4, rec))
        assert (y + 4 + 22) + 8 <= top - 8 - 10  # >= 8 units above the lane labels' cap height
        for k in range(3):
            ty = top + 8 + 31 * k
            P.append(ghosts(k, (lx0 + 8, ty), (lx0 + lw + gap + 8, ty), tw, rec))
            P.append(token(lx0 + 2 * (lw + gap) + 8, ty, tw, k, (-2 * (lw + gap), 0), (-(lw + gap), 0), rec, (ty, ty + 26)))
    else:
        P.append(f'<text class="sub f-vasp-pm" x="{f(x + 16)}" y="{f(y + 44)}">sbatch over SSH</text>')
        bh, gap, top = 58, 8, y + 58
        tw = (w - 24 - 2 * 8) / 3
        for i, name in enumerate(LANES):
            ly = top + i * (bh + gap)
            P.append(f'<rect class="f-vasp-lane" x="{f(x + 12)}" y="{f(ly)}" width="{f(w - 24)}" height="{bh}" rx="8"/>'
                     f'<text class="tag f-vasp-pk" x="{f(x + 22)}" y="{f(ly + 20)}">{name}</text>')
        ly = top + 2 * (bh + gap)
        P.append(potcar(x + w - 16 - 88, y + 26, rec))
        assert y + 26 + 22 + 8 <= top
        for k in range(3):
            tx = x + 12 + k * (tw + 8)
            P.append(ghosts(k, (tx, top + 27), (tx, top + bh + gap + 27), tw, rec))
            P.append(token(tx, ly + 27, tw, k, (0, -2 * (bh + gap)), (0, -(bh + gap)), rec, (top + 27, ly + 53)))
        assert 10 + max(map(len, JOBS)) * CW["narrow"] + 26 <= tw
    toks = [m for m in P[3:] if not m.startswith('<rect class="f-vasp-lane"')]
    lanes = [m for m in P[3:] if m.startswith('<rect class="f-vasp-lane"')]
    return (rv(f'<g class="f-vasp-pnl">{"".join(P[:3])}</g>', T["cluster"], rec, y, y + h, d=.4)
            + rv("".join(lanes), T["cluster"] + .15, rec, y, y + h) + "".join(toks))


def fetch_dots(x, y0, y1, rec):
    """One dot per job down the cluster -> parser connector, after that job's tick (hidden at rest)."""
    out = []
    for k in range(3):
        t = T["tok0"] + TOK_PITCH * k + TOK["fetch"]
        rec(t, TOK["end"] - TOK["fetch"], y0, y1)
        out.append(f'<circle class="f-vasp-fp" cx="{f(x)}" cy="{f(y0)}" r="4" opacity="0" data-t="{_tv(t)}" data-l="{f(y1 - y0)}"/>')
    return "".join(out)


# ----------------------------------------------------------------------------------------------- (c) results ----
CHIPS = ["OUTCAR", "vasprun.xml", "CONTCAR", "DOSCAR", "EIGENVAL"]


def chips(xr, y, rec, wide, rows=1):
    """Parser chips, right-aligned to xr; rows=2 splits them 3 + 2."""
    cw = CW["wide" if wide else "narrow"]
    groups = [CHIPS] if rows == 1 else [CHIPS[:3], CHIPS[3:]]
    P, k = [], 0
    for r, g in enumerate(groups):
        ws = [len(c) * cw + 18 for c in g]
        x = xr - sum(ws) - 8 * (len(g) - 1)
        for c, w in zip(g, ws):
            yy = y + r * 32
            P.append(rv(f'<g class="f-vasp-chip"><rect x="{f(x)}" y="{f(yy)}" width="{f(w)}" height="24" rx="6"/>'
                        f'<text class="sub" x="{f(x + w / 2)}" y="{f(yy + 16.5)}" text-anchor="middle">{c}</text></g>',
                        T["chip0"] + .06 * k, rec, yy, yy + 24, dy=6))
            x += w + 8
            k += 1
    return "".join(P)


def _card(x, y, w, h, tag, t, rec, inner, cls=""):
    head = (f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>'
            f'<text class="tag" x="{f(x + 14)}" y="{f(y + 22)}">{tag}</text>')
    return f'<g class="card {cls}">{head}</g>' + inner


def ads_card(x, y, w, h, rec, wide):
    t = T["ads"]
    terms = ["E(slab+CO)", "− E(slab)", "− E(CO, gas)"]
    if wide:
        tl = [(x + 14, y + 72 + 20 * k) for k in range(3)]
        vx, vy, anchor = x + 14, y + 168, "start"
        tail = f'<text class="sub" x="{f(x + 14)}" y="{f(y + h - 14)}">from the 3 jobs above</text>'
    else:
        tl = [(x + 14, y + 68 + 18 * k) for k in range(3)]
        vx, vy, anchor = x + w - 14, y + 96, "end"
        tail = ""
    inner = [rv(f'<text class="ttl{"" if wide else " sm"}" x="{f(x + 14)}" y="{f(y + 46)}">Adsorption energy</text>', t + .1, rec, y + 32, y + 50)]
    for k, ((tx, ty), s) in enumerate(zip(tl, terms)):
        inner.append(rv(f'<text class="sub f-vasp-ink" x="{f(tx)}" y="{f(ty)}">{escape(s)}</text>', t + .2 + .12 * k, rec, ty - 12, ty + 4, dx=-8))
    inner.append(rv(f'<text class="f-vasp-big" x="{f(vx)}" y="{f(vy)}" text-anchor="{anchor}">{E_ADS}{NB}eV</text>'
                    + (tail if tail else ""), t + .65, rec, vy - 26, (y + h) if tail else vy + 4, d=.35))
    return _card(x, y, w, h, "VW 9.4 · ADSORPTION", t, rec, "".join(inner), "f-vasp-ads")


def _plot(x, y, w, h):
    """Plot box inside a result card: left margin for tick labels, returns px0, px1, py0, py1."""
    return x + 44, x + w - 18, y + 48, y + h - 82


def _hermite(ys, n=10):
    """Points (s, E) of a cubic Hermite spline through ys at s = k/(len-1); end tangents 0 (minima)."""
    m = [0.0] + [(ys[k + 1] - ys[k - 1]) / 2 for k in range(1, len(ys) - 1)] + [0.0]
    out = []
    for k in range(len(ys) - 1):
        for i in range(n + (1 if k == len(ys) - 2 else 0)):
            u = i / n
            h00, h10, h01, h11 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u, -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
            out.append(((k + u) / (len(ys) - 1), h00 * ys[k] + h10 * m[k] + h01 * ys[k + 1] + h11 * m[k + 1]))
    return out


NEB_PATH = _hermite(NEB_E)
NEB_T = {"guide": .2, "beads": .25, "relax": .6, "climb": .85, "path": 1.2, "ci": 1.3, "arrow": 1.45, "subs": 1.55}
NEB_RELAX = .35  # a bead's relax duration
NEB_BUMP = .18  # eV: the interpolated guess lies above the minimum-energy path (largest mid-path); relaxing lowers it
# images appear before any relaxes; the CI starts after the others and finishes last; the path is drawn after
assert NEB_T["beads"] + .04 * 6 + .1 <= NEB_T["relax"] < NEB_T["climb"]
assert NEB_T["relax"] + NEB_RELAX < NEB_T["climb"] + NEB_RELAX <= NEB_T["path"]
assert max(e for _, e in NEB_PATH) <= max(NEB_E) + 1e-9  # no overshoot above the climbing image


def neb_card(x, y, w, h, rec, wide):
    t = T["neb"]
    px0, px1, py0, py1 = _plot(x, y, w, h)
    lo, hi = -0.32, 0.92
    assert max(NEB_E) + NEB_BUMP < hi
    X = lambda s: px0 + s * (px1 - px0)
    Y = lambda e: py1 - (e - lo) / (hi - lo) * (py1 - py0)
    P = []
    axes = (f'<path class="f-vasp-ax" d="M{f(px0 - 8)},{f(py0 - 4)} V{f(py1 + 6)} H{f(px1 + 6)}"/>'
            f'<path class="f-vasp-ref" d="M{f(px0)},{f(Y(0))} H{f(px1)}"/>'
            f'<text class="sub" x="{f(x + 14)}" y="{f(y + 40)}">eV</text>'
            f'<text class="sub" x="{f(px0 - 14)}" y="{f(Y(0) + 4.5)}" text-anchor="end">0</text>'
            f'<text class="sub" x="{f(px0 - 14)}" y="{f(Y(.5) + 4.5)}" text-anchor="end">0.5</text>'
            f'<path class="f-vasp-ax" d="M{f(px0 - 11)},{f(Y(.5))} h3"/>'
            f'<text class="sub" x="{f(px0)}" y="{f(py1 + 24)}" text-anchor="middle">IS</text>'
            f'<text class="lbl" x="{f((px0 + px1) / 2)}" y="{f(py1 + 24)}" text-anchor="middle">reaction coordinate</text>'
            f'<text class="sub" x="{f(px1)}" y="{f(py1 + 24)}" text-anchor="middle">FS</text>')
    P.append(rv(axes, t + .1, rec, y + 28, py1 + 28))
    # the images start at the interpolated guess between the relaxed end points, above the minimum-energy path
    # (dashed, shown only while they relax); optimisation lowers each onto the path, the climbing image settling
    # last at the saddle; then the path is drawn through them
    guess = lambda s, e: e + NEB_BUMP * math.sin(math.pi * s)
    gd = "M" + " L".join(f"{f(X(s_))},{f(Y(guess(s_, e_)))}" for s_, e_ in NEB_PATH)
    P.append(f'<path class="f-vasp-guide" d="{gd}" opacity="0" '
             f'data-t="{_tv(t + NEB_T["guide"])}" data-t2="{_tv(t + NEB_T["climb"] + .1)}"/>')
    for k, e in enumerate(NEB_E):
        bx, by = X(k / 6), Y(e)
        tb, t2 = t + NEB_T["beads"] + .04 * k, t + (NEB_T["climb"] if k == CI else NEB_T["relax"])
        rec(t2, NEB_RELAX, py0, py1)
        assert Y(guess(k / 6, e)) <= by  # relaxing moves every image down (or keeps an end point)
        cls = "f-vasp-bead end" if k in (0, 6) else "f-vasp-bead"
        P.append(f'<g class="{cls}" data-t="{_tv(tb)}" data-t2="{_tv(t2)}" data-dy="{f(Y(guess(k / 6, e)) - by)}">'
                 f'<circle cx="{f(bx)}" cy="{f(by)}" r="5.5"/></g>')
    d = "M" + " L".join(f"{f(X(s))},{f(Y(e))}" for s, e in NEB_PATH)
    P.append(dr(d, t + NEB_T["path"], rec, py0, py1, "f-vasp-path", dur=.4))
    cx_, cy_ = X(CI / 6), Y(NEB_E[CI])
    ci = (f'<circle class="f-vasp-ci" cx="{f(cx_)}" cy="{f(cy_)}" r="9.5"/>'
          f'<text class="sub f-vasp-acc" x="{f(cx_)}" y="{f(cy_ - 13)}" text-anchor="middle">CI</text>')  # above: the path falls away on both sides
    P.append(rv(ci, t + NEB_T["ci"], rec, cy_ - 10, cy_ + 10))
    # the arrowhead marker would show before the line is drawn, so the arrow fades in instead
    P.append(rv(f'<path class="f-vasp-bar" d="M{f(cx_)},{f(Y(0) - 1)} V{f(cy_ + 12)}" marker-end="url(#arr)"/>', t + NEB_T["arrow"], rec, cy_, Y(0), d=.2, dy=6))
    subs = [("IDPP · climbing image", ""), (f"barrier 0.62{NB}eV", " f-vasp-acc")]
    sy = [py1 + 46 + 19 * k for k in range(2)]
    P.append(rv("".join(f'<text class="sub{c}" x="{f(x + 14)}" y="{f(yy)}">{s}</text>' for (s, c), yy in zip(subs, sy)),
                t + NEB_T["subs"], rec, sy[0] - 12, sy[-1] + 4))
    return _card(x, y, w, h, "VW 9.5 · NEB", t, rec, "".join(P), "f-vasp-neb")


def eos_card(x, y, w, h, rec, wide):
    t = T["eos"]
    px0, px1, py0, py1 = _plot(x, y, w, h)
    vlo, vhi, elo, ehi = 10.95, 13.05, -3.0, 40.0
    X = lambda v: px0 + (v - vlo) / (vhi - vlo) * (px1 - px0)
    Y = lambda e: py1 - (e - elo) / (ehi - elo) * (py1 - py0)
    assert max(e for _, e in EOS_PTS) < ehi
    P = []
    axes = (f'<path class="f-vasp-ax" d="M{f(px0 - 8)},{f(py0 - 4)} V{f(py1 + 6)} H{f(px1 + 6)}"/>'
            f'<text class="sub" x="{f(x + 14)}" y="{f(y + 40)}">E − E₀ (meV/atom)</text>'
            f'<text class="sub" x="{f(px0 - 14)}" y="{f(Y(0) + 4.5)}" text-anchor="end">0</text>'
            f'<text class="sub" x="{f(px0 - 14)}" y="{f(Y(30) + 4.5)}" text-anchor="end">30</text>'
            f'<path class="f-vasp-ax" d="M{f(px0 - 11)},{f(Y(30))} h3"/>'
            f'<text class="sub" x="{f(X(11))}" y="{f(py1 + 24)}" text-anchor="middle">11</text>'
            f'<text class="lbl" x="{f((px0 + px1) / 2)}" y="{f(py1 + 24)}" text-anchor="middle">V per atom (Å³)</text>'
            f'<text class="sub" x="{f(X(13))}" y="{f(py1 + 24)}" text-anchor="middle">13</text>')
    P.append(rv(axes, t + .1, rec, y + 28, py1 + 28))
    for k, (v, e) in enumerate(EOS_PTS):
        P.append(rv(f'<circle class="f-vasp-ept" cx="{f(X(v))}" cy="{f(Y(e))}" r="4.5"/>', t + .25 + .05 * k, rec, py0, py1,
                    d=.25, dy=-10))
    v_lo = 11.07  # the fit starts just outside the first point and stays below the plot top
    vs = [v_lo + (13.02 - v_lo) * i / 40 for i in range(41)]
    assert max(bm(v) * 1000 for v in vs) < ehi - 2 and v_lo < EOS_V[0]
    fit = " L".join(f"{f(X(v))},{f(Y(bm(v) * 1000))}" for v in vs)
    mean = sum(e for _, e in EOS_PTS) / len(EOS_PTS)
    flat = " L".join(f"{f(X(v))},{f(Y(mean))}" for v in vs)
    tf = t + .75
    rec(tf, .45, py0, py1)
    P.append(f'<g class="f-vasp-rv" data-t="{_tv(tf - .05)}" data-d="0.1"><path class="f-vasp-fit" d="M{fit}" data-d0="M{flat}" data-t="{_tv(tf)}"/></g>')
    # top right is clear of both arms (the expansion side rises slowly) and of the y-axis label
    P.append(rv(f'<text class="lbl" x="{f(px1)}" y="{f(py0 + 12)}" text-anchor="end">Birch–Murnaghan</text>', tf + .3, rec, py0, py0 + 16))
    vx = X(V0)
    P.append(rv(f'<path class="f-vasp-v0" d="M{f(vx)},{f(Y(0) - 8)} V{f(py1 + 6)}"/>'
                f'<text class="sub f-vasp-acc" x="{f(vx + 6)}" y="{f(Y(0) - 10)}">V₀</text>', tf + .45, rec, Y(0) - 22, py1 + 6))
    subs = [(f"V₀ 12.0{NB}Å³, B₀ 140{NB}GPa", " f-vasp-acc"), ("B₀′ 5.0", "")]
    sy = [py1 + 46 + 19 * k for k in range(2)]
    for (s, _), yy in zip(subs, sy):
        assert len(s) <= 22, s
    P.append(rv("".join(f'<text class="sub{c}" x="{f(x + 14)}" y="{f(yy)}">{s}</text>' for (s, c), yy in zip(subs, sy)),
                tf + .55, rec, sy[0] - 12, sy[-1] + 4))
    return _card(x, y, w, h, "VW 9.7 · EOS · Cu", t, rec, "".join(P), "f-vasp-eos")


def dos_card(x, y, w, h, rec, wide):
    t = T["dos"]
    px0, px1, py0, py1 = _plot(x, y, w, h)
    lo, hi, dmax = -8.0, 3.0, 3.0
    X = lambda e: px0 + (e - lo) / (hi - lo) * (px1 - px0)
    Y = lambda g: py1 - g / dmax * (py1 - py0)
    es = [lo + (hi - lo) * i / 110 for i in range(111)]
    line = " L".join(f"{f(X(e))},{f(Y(dos(e)))}" for e in es)
    P = []
    axes = (f'<path class="f-vasp-ax" d="M{f(px0 - 8)},{f(py0 - 4)} V{f(py1 + 6)} H{f(px1 + 6)}"/>'
            f'<text class="sub" x="{f(x + 14)}" y="{f(y + 40)}">states/eV</text>'
            + "".join(f'<path class="f-vasp-ax" d="M{f(X(e))},{f(py1 + 6)} v4"/>' for e in (-6, -3, 0))
            + "".join(f'<text class="sub" x="{f(X(e))}" y="{f(py1 + 24)}" text-anchor="middle">{s}</text>' for e, s in ((-6, "−6"), (0, "0")))
            + f'<text class="lbl" x="{f(X(-3))}" y="{f(py1 + 24)}" text-anchor="middle">E − E<tspan dy="3">F</tspan><tspan dy="-3"> (eV)</tspan></text>')
    P.append(rv(axes, t + .1, rec, y + 28, py1 + 28))
    P.append(rv(f'<path class="f-vasp-dosf" d="M{f(X(lo))},{f(Y(0))} L{line} L{f(X(hi))},{f(Y(0))} Z"/>', t + .75, rec, py0, py1, d=.35))
    P.append(dr(f"M{line}", t + .2, rec, py0, py1, "f-vasp-dos", dur=.6))
    fx = X(0)
    P.append(rv(f'<path class="f-vasp-ef" d="M{f(fx)},{f(py0 - 2)} V{f(py1 + 6)}"/>'
                f'<text class="lbl" x="{f(fx)}" y="{f(py0 - 8)}" text-anchor="middle">Fermi level</text>', t + .85, rec, py0 - 20, py1))
    subs = [("DOSCAR · EIGENVAL", ""), (f"band gap 0{NB}eV (metal)", " f-vasp-acc")]
    sy = [py1 + 46 + 19 * k for k in range(2)]
    for (s, _), yy in zip(subs, sy):
        assert len(s) <= 22, s
    P.append(rv("".join(f'<text class="sub{c}" x="{f(x + 14)}" y="{f(yy)}">{s}</text>' for (s, c), yy in zip(subs, sy)),
                t + 1.05, rec, sy[0] - 12, sy[-1] + 4))
    return _card(x, y, w, h, "VW 9.3 · DOS · Cu", t, rec, "".join(P), "f-vasp-dosc")


LABEL = ("VASP workflows, VW 9.1–9.7, in three panels. (a) Structure bench: a Cu(111) slab is built from bulk copper and "
         f"the Miller index (111), with 15{NB}Å of vacuum, and CO is placed on an ontop site. Each step writes INCAR (a "
         "preset for its workflow, ENCUT 1.3 times the largest ENMAX), POSCAR and KPOINTS (a Γ-centred mesh), returned "
         "for review. (b) Governed queue: "
         "one approval per run, in chat or the Approval Inbox, shows the planned steps, the first step's inputs, the "
         "Slurm profile and a core-hour ceiling, and a step outside the plan asks again. Until you approve, a gate holds "
         "the jobs; then the steps are submitted in order with sbatch over SSH, each after the previous one completes, and "
         "each Slurm job goes from PENDING to RUNNING to COMPLETED, leaving its elapsed time. POTCAR is assembled on the "
         "cluster from your licensed set and never leaves it. Each finished job's folder is fetched and parsed before "
         "the next job is submitted. A failed state keeps Slurm's reason and is not "
         "resubmitted. (c) Results, fetched and "
         "parsed from OUTCAR, vasprun.xml, CONTCAR, DOSCAR and EIGENVAL: the adsorption energy, E(slab+CO) minus E(slab) "
         f"minus E(CO), {E_ADS}{NB}eV. NEB, EOS and DOS are each their own run through the same queue: NEB images "
         "interpolated between the relaxed end points relax down onto the minimum-energy path, the climbing image "
         "settling last at the saddle, with "
         f"a barrier of 0.62{NB}eV; equation-of-state energies, relative to the minimum energy, fitted with the "
         "Birch–Murnaghan equation, giving the equilibrium volume, V zero, "
         f"12.0{NB}Å³ per atom, the bulk modulus, B zero, 140{NB}GPa, and its pressure derivative, B zero prime, 5.0; "
         "and the DOS of copper against energy relative to the Fermi energy, with no band gap. "
         "All values are illustrative.")
LEGEND = [("amber", "waits for your approval"), ("okc", "Slurm job completed"), ("flow", "submitted after approval"),
          ("dash", "POTCAR: stays on the cluster")]


# ---------------------------------------------------------------------------------------------------- layouts ----
WIDE = {"W": 1100, "H": 760}
VIS = {"pad": 27, "below": 64, "header": 69}  # figure border+padding; below the SVG (padding, caption); sticky header


def _wide():
    W, H, pre, rec = WIDE["W"], WIDE["H"], "vasp-w", Rec()
    P = [_defs(pre), rv(hdr(30, 34, "VASP WORKFLOWS · VW 9.1–9.7"), T["head"], rec, 20, 38)]
    # (a) bench
    P.append(rv(badge(30, 80, "a", "STRUCTURE BENCH"), T["ahead"], rec, 66, 84))
    X, CT, TL = 70, 112, 268
    sl, cb = slab(pre, X, CT, TL, rec, True)
    P.append(sl)
    FX, FW, FH, FP = 322, 194, 54, 84
    fy = [118 + FP * k for k in range(3)]
    assert fy[-1] + FH <= cb + 2
    ox, oy = X + CELL_W + 4, TL + 2 * DZ
    for k, y in enumerate(fy):
        P.append(rv(f'<path class="cv f-vasp-fan" d="{curve_d(ox, oy, FX - 2, y + FH / 2)}" marker-end="url(#arr)"/>',
                    T["fan"] + .04 * k, rec, min(oy, y + FH / 2), max(oy, y + FH / 2), d=.25))
        P.append(file_card(FX, y, FW, FH, k, rec, True))
    # the three written files: a brace, then on to the approval (shown) and the gate (submitted)
    bx, b0, b1 = FX + FW + 6, fy[0] + 2, fy[2] + FH - 2
    bm_ = (b0 + b1) / 2
    brace = (f'<path class="f-vasp-brace" d="M{f(bx)},{f(b0)} q6,0 6,8 V{f(bm_ - 8)} q0,8 6,8 q-6,0 -6,8 V{f(b1 - 8)} q0,8 -6,8"/>')
    AX, AY, AW, AH = 562, 108, 508, 100
    GX, GY, GW, GH = 584, 228, 22, 148
    CX, CY, CWd, CH = 618, 218, 452, 162
    conn_show = curve_d(bx + 14, bm_, AX - 2, AY + 46)
    conn_go = curve_d(bx + 14, bm_, GX - 4, GY + 80)
    P.append(rv(brace + f'<path class="cv" d="{conn_show}" marker-end="url(#arr)"/>'
                f'<path class="cv" d="{conn_go}" marker-end="url(#arr)"/>', T["conn"], rec, AY, GY + 84))
    # (b) queue
    P.append(rv(badge(AX, 80, "b", "GOVERNED QUEUE"), T["bhead"], rec, 66, 84))
    P.append(approval(AX, AY, AW, AH, rec, True))
    gx = GX + GW / 2
    P.append(rv(f'<path class="cv f-vasp-wait" d="M{f(gx)},{f(AY + AH + 2)} V{f(GY - 2)}"/>', T["appr"], rec, AY + AH, GY))
    P.append(dr(f"M{f(gx)},{f(AY + AH + 2)} V{f(GY - 2)}", T["ok2gate"], rec, AY + AH, GY, "f-vasp-fl", dur=.12))
    P.append(dr(conn_go, T["flow"], rec, bm_, GY + 80, "f-vasp-fl", dur=.25))
    P.append(cluster(pre, CX, CY, CWd, CH, True, rec))
    P.append(gate(pre, GX, GY, GW, GH, True, rec))
    P.append(rv(f'<text class="lbl amb" x="{f(CX)}" y="{f(CY + CH + 22)}">failed state: Slurm&#39;s reason kept, not resubmitted</text>',
                T["fail"], rec, CY + CH + 8, CY + CH + 26))
    # (c) results
    RY = 440
    P.append(rv(badge(30, RY, "c", "RESULTS · FETCHED AND PARSED"), T["chead"], rec, RY - 14, RY + 4))
    lane3 = CX + 12 + 2 * ((CWd - 40) / 3 + 8) + (CWd - 40) / 6
    P.append(rv(f'<path class="cv" d="M{f(lane3)},{f(CY + CH + 2)} V{f(RY - 18)}" marker-end="url(#arr)"/>', T["parse"], rec, CY + CH, RY - 16, d=.1))
    P.append(fetch_dots(lane3, CY + CH + 4, RY - 20, rec))
    P.append(chips(1070, RY - 14, rec, True))
    P.append(rv(f'<text class="lbl" x="348" y="{f(RY)}">NEB, EOS and DOS: own runs, same queue</text>', T["cue"], rec, RY - 12, RY + 4))
    cy, chh = 474, 222
    P.append(ads_card(30, cy, 222, chh, rec, True))
    P.append(neb_card(268, cy, 258, chh, rec, True))
    P.append(eos_card(542, cy, 258, chh, rec, True))
    P.append(dos_card(816, cy, 254, chh, rec, True))
    P.append(legend(LEGEND, 30, H - 34) + note(30, H - 8))
    _check_scroll(rec, H)
    return svg(W, H, "".join(P), "wide", LABEL)


def _check_scroll(rec, H):
    """Each element finishes inside the viewport (below the sticky header) at the scroll position where the scrub
    reaches its end time. Runtime range: figure top at 80 % of the viewport -> figure centre at 45 %."""
    for vh in (650, 700, 800, 900):
        for k in (0.831, 0.94):  # SVG px per unit at 1000 px and >= 1280 px
            hfig = VIS["pad"] + H * k + VIS["below"]
            travel = 0.35 * vh + hfig / 2
            for t_end, y0, y1 in rec.items:
                top = 0.8 * vh - travel * min(1, t_end / T_END)
                assert top + VIS["pad"] + y1 * k <= vh + .5, (vh, k, t_end, y1)
                assert top + VIS["pad"] + y0 * k >= VIS["header"], (vh, k, t_end, y0)


def _narrow():
    W, pre, rec = 360, "vasp-n", Rec()
    P = [_defs(pre), rv(hdr(16, 24, "VASP WORKFLOWS · VW 9.1–9.7"), T["head"], rec, 0, 0)]
    P.append(rv(badge(16, 64, "a", "STRUCTURE BENCH"), T["ahead"], rec, 0, 0))
    X, CT = 84, 82
    TL = CT + 140
    sl, cb = slab(pre, X, CT, TL, rec, False)
    P.append(sl)
    FX, FW, FH, FP = 60, 284, 58, 68
    fy0 = cb + 26
    fy = [fy0 + FP * k for k in range(3)]
    tx_, ox = 34, X + 16
    for k, y in enumerate(fy):
        ym = y + FH / 2
        cls = "cv f-vasp-fan"
        d = (f"M{f(ox)},{f(cb + 2)} C{f(ox)},{f(cb + 16)} {f(tx_)},{f(cb + 8)} {f(tx_)},{f(cb + 24)} V{f(ym - 14)} "
             f"C{f(tx_)},{f(ym - 3)} {f(tx_ + 6)},{f(ym)} {f(FX - 2)},{f(ym)}")
        P.append(rv(f'<path class="{cls}" d="{d}" marker-end="url(#arr)"/>', T["fan"] + .04 * k, rec, 0, 0, d=.25))
        P.append(file_card(FX, y, FW, FH, k, rec, False))
    # the three written files feed the approval card
    AY = fy[-1] + FH + 58
    P.append(rv(badge(16, AY - 18, "b", "GOVERNED QUEUE"), T["bhead"], rec, 0, 0))
    bx, b0, b1 = FX + FW + 2, fy[0] + 2, fy[2] + FH - 2
    bm_ = (b0 + b1) / 2
    brace = f'<path class="f-vasp-brace" d="M{f(bx)},{f(b0)} q3,0 3,8 V{f(bm_ - 8)} q0,8 3,8 q-3,0 -3,8 V{f(b1 - 8)} q0,8 -3,8"/>'
    P.append(rv(brace + f'<path class="cv" d="M{f(bx + 7)},{f(bm_)} V{f(AY - 22)} C{f(bx + 7)},{f(AY - 8)} 330,{f(AY - 14)} 330,{f(AY - 2)}" '
                'marker-end="url(#arr)"/>', T["conn"], rec, 0, 0))
    AH = 184
    P.append(approval(16, AY, 328, AH, rec, False))
    GX, GY, GW, GH = 16, AY + AH + 22, 328, 18
    gy_c = GY + GH / 2
    P.append(rv(f'<path class="cv f-vasp-wait" d="M180,{f(AY + AH + 2)} V{f(GY + GH + 26)}" marker-end="url(#arr)"/>', T["appr"], rec, 0, 0))
    P.append(dr(f"M180,{f(AY + AH + 2)} V{f(GY + GH + 26)}", T["flow"], rec, 0, 0, "f-vasp-fl", dur=.25))
    CY = GY + GH + 30
    CH = 58 + 3 * 58 + 2 * 8 + 12
    P.append(cluster(pre, 16, CY, 328, CH, False, rec))
    P.append(gate(pre, GX + 30, GY, GW - 30, GH, False, rec))
    P.append(rv(f'<text class="lbl amb" x="16" y="{f(CY + CH + 24)}">failed state: reason kept, no resubmit</text>', T["fail"], rec, 0, 0))
    RY = CY + CH + 74
    P.append(rv(badge(16, RY, "c", "FETCHED · PARSED"), T["chead"], rec, 0, 0))
    P.append(rv(f'<path class="cv" d="M320,{f(CY + CH + 2)} V{f(RY + 6)}" marker-end="url(#arr)"/>', T["parse"], rec, 0, 0, d=.1))
    P.append(fetch_dots(320, CY + CH + 4, RY + 4, rec))
    P.append(chips(344, RY + 10, rec, False, rows=2))
    cue_y = RY + 10 + 32 + 24 + 20
    P.append(rv(f'<text class="lbl" x="16" y="{f(cue_y)}">NEB, EOS and DOS: own runs, same queue</text>', T["cue"], rec, 0, 0))
    y = cue_y + 16
    P.append(ads_card(16, y, 328, 116, rec, False))
    y += 116 + 16
    for fn in (neb_card, eos_card, dos_card):
        P.append(fn(16, y, 328, 214, rec, False))
        y += 214 + 16
    ly = y + 16
    P.append("".join(legend([it], 16, ly + 24 * k) for k, it in enumerate(LEGEND)) + note(16, ly + 24 * 4 + 4))
    H = ly + 24 * 4 + 18
    return svg(W, H, "".join(P), "narrow", LABEL)


JS = """MAFig.register("vasp", function (root, variant) {
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var one = function (s) { return root.querySelector(s); };
  var T = function (el) { return +el.getAttribute("data-t"); };
  var num = function (el, a) { return +(el.getAttribute(a) || 0); };
  var pair = function (el, a) { return el.getAttribute(a).split(" ").map(Number); };
  // origins set once, at scale 1 (an origin passed per tween is smoothed against the from-scale)
  gsap.set(q(".f-vasp-okb, .f-vasp-tick, .f-vasp-gok, .f-vasp-gokc"), {transformOrigin: "50% 50%"});
  var tl = gsap.timeline({defaults: {ease: "power2.out"}});
  // (a) the cell's vacuum and layers, CO lowered onto its site, the input files fanning out; generic reveals at
  // their own times, connectors drawn on
  q(".f-vasp-rv").forEach(function (el) {
    tl.from(el, {opacity: 0, x: num(el, "data-dx"), y: num(el, "data-dy"), duration: +(el.getAttribute("data-d") || .3)}, T(el));
  });
  q(".f-vasp-dr").forEach(function (el) {
    tl.from(el, {drawSVG: "0%", duration: +el.getAttribute("data-d"), ease: "none"}, T(el));
  });
  // (b) Approve is pressed; only then do the gate's bars retract and the jobs enter
  var okb = one(".f-vasp-okb"), bars = one(".f-vasp-bars");
  tl.from(okb, {opacity: 0, scale: 0, duration: .2, ease: "back.out(2.5)"}, T(okb))
    .from(bars, {x: num(bars, "data-dx"), y: num(bars, "data-dy"), duration: .35, ease: "power2.in"}, T(bars));
  // one job per step, in order (the next enters only after this one is COMPLETED): PENDING, RUNNING (an
  // indeterminate pulse: Slurm reports no progress within a job), COMPLETED, then the tick
  q(".f-vasp-tok").forEach(function (k) {
    var t = T(k), p = pair(k, "data-p"), r = pair(k, "data-r"), run = k.querySelector(".f-vasp-run"),
      tick = k.querySelector(".f-vasp-tick");
    tl.fromTo(k, {x: p[0], y: p[1], opacity: 0}, {x: p[0], y: p[1], opacity: 1, duration: .1}, t)
      .to(k, {x: r[0], y: r[1], duration: .12, ease: "power2.inOut"}, t + __RUN__)
      .set(run, {opacity: 1}, t + __PULSE__)
      .fromTo(run, {x: 0}, {x: num(run, "data-tr"), duration: .12, repeat: 1, yoyo: true, ease: "sine.inOut"}, t + __PULSE__)
      .set(run, {opacity: 0}, t + __DONE__)
      .to(k, {x: 0, y: 0, duration: .12, ease: "power2.inOut"}, t + __DONE__)
      .from(tick, {opacity: 0, scale: 0, duration: .12, ease: "back.out(2.5)"}, t + __TICK__);
  });
  // each finished job's folder is fetched and parsed before the next job is submitted: a dot runs to the parsers
  q(".f-vasp-fp").forEach(function (d) {
    var t = T(d);
    tl.set(d, {opacity: 1, y: 0}, t).to(d, {y: num(d, "data-l"), duration: __FETCH__, ease: "power1.in"}, t)
      .set(d, {opacity: 0}, t + __FETCH__);
  });
  // (c) NEB: the images appear on the interpolated line between the relaxed end points, relax onto their
  // energies (the climbing image last); the guide line fades as they go
  q(".f-vasp-guide").forEach(function (g) {
    tl.fromTo(g, {opacity: 0}, {opacity: 1, duration: .2}, T(g)).to(g, {opacity: 0, duration: .25}, num(g, "data-t2"));
  });
  q(".f-vasp-bead").forEach(function (b) {
    var dy = num(b, "data-dy");
    tl.fromTo(b, {y: dy, opacity: 0}, {y: dy, opacity: 1, duration: .1}, T(b))
      .to(b, {y: 0, duration: __RELAX__, ease: "power2.inOut"}, num(b, "data-t2"));
  });
  // EOS: a flat start bends into the Birch–Murnaghan fit through the points
  var fit = one(".f-vasp-fit");
  tl.from(fit, {attr: {d: fit.getAttribute("data-d0")}, duration: .45, ease: "power2.inOut"}, T(fit));
  tl.set({}, {}, __END__);
  if (variant === "narrow") tl.timeScale(1.4);  // narrow plays once, not scrubbed
  return {intro: tl};
}, {scrub: true});"""
for _k, _v in {"__END__": T_END, "__RUN__": TOK["run"], "__PULSE__": TOK["pulse"], "__DONE__": TOK["done"],
               "__TICK__": TOK["tick"], "__FETCH__": TOK["end"] - TOK["fetch"],
               "__RELAX__": NEB_RELAX}.items():
    JS = JS.replace(_k, _tv(_v))
assert "__" not in JS


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
