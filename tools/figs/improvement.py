"""Improvement figure: improves and extends itself (claims C30, C32, C43, C48, C51, C54, C67, C69, C70, C71).
(a) An improvement run on a live score plot (C30, C69): the baseline is measured, 12 candidates are scored on the 20 %
subset (stage 1) and the top third move on to the whole select split (stage 2); up to three above the baseline's select
mean take holdout confidence intervals against the baseline's holdout mean plus a margin (stage 3); the one whose lower
bound clears waits for an administrator, and only then becomes active. A dashed side path: for DISCOVER's own program,
approval writes a local git branch (C32).
(b) The self-extension bench: a plain-language description (C48) -> library search over the registry, PyPI and GitHub,
ranked by relevance (C54) -> the generated module and its tests type into the editor (the one dark focal panel) ->
syntax, import, type, lint and contract checks, then the tests in an isolated runner (C43) -> files staged only once the
checks pass, promotion a separate step (C51, C70) -> readiness (ARS) only once test and security results exist (C67).
Beside it OpenEvolve (C71): five islands drawn as contour maps, each new program a dot placed by its fitness (summit =
higher fitness), the best one marked at the end. Migration is not drawn (not claimed). Values are illustrative."""
import math
import random
from html import escape

from figkit import Figure, curve, curve_d, f, hdr, legend, note, svg, vcurve_d

CW = {"wide": 7.68, "narrow": 8.04}  # Geist Mono advance per character at the sub size
TW = {"wide": 9.22, "narrow": 9.65}  # tag advance (0.6 em + .12 em letter-spacing)
HW = {"wide": 9.73, "narrow": 10.18}  # header advance (0.6 em + .16 em letter-spacing)
LBL = {"wide": 12.8 * .52, "narrow": 13.4 * .52}  # Geist italic advance per character (line labels)
OKW = {"wide": 12.8 * .58, "narrow": 13.4 * .58}  # Geist 600 advance per character (.lbl.ok)
TTL_SM = 13.5 * .58
NB = " "  # narrow no-break space before %

# --- (a) the improvement run (C30, C69); scores 0.4-0.9, illustrative ------------------------------------------------
S1 = [.55, .68, .60, .72, .50, .66, .58, .70, .63, .52, .69, .57]  # stage 1: 20 % subset of the select split
S2 = {1: .69, 3: .74, 7: .71, 10: .64}  # stage 2: the whole select split (the top third only)
BASE_SEL, BASE_HOLD, MARGIN = .66, .63, .04
HOLD = {3: (.75, .69, .81), 7: (.70, .62, .78), 1: (.68, .60, .76)}  # holdout mean, CI low, CI high
KEEP = sorted(range(12), key=lambda i: -S1[i])[:math.ceil(12 / 3)]
ABOVE = sorted((i for i in KEEP if S2[i] > BASE_SEL), key=lambda i: -S2[i])[:3]
WIN = [i for i in ABOVE if HOLD[i][1] > BASE_HOLD + MARGIN]
assert set(S2) == set(KEEP) and set(HOLD) == set(ABOVE) and WIN == [3], (KEEP, ABOVE, WIN)
KIND = [2 if i in ABOVE else 1 if i in KEEP else 0 for i in range(12)]  # 0 out at stage 1, 1 out at stage 2, 2 holdout
FINAL = [HOLD[i][0] if k == 2 else S2[i] if k == 1 else S1[i] for i, k in enumerate(KIND)]

STEPS = [("Baseline", "measured first", ""), ("12 candidates", "proposed by a model", ""),
         ("Holdout", "CI low > mean + margin", ""), ("Approval", "by an administrator", "amb"),
         ("Active", "becomes the default", "ok")]

# --- (b) the bench (C43, C48, C51, C54, C67, C70) -------------------------------------------------------------------
DESC_W = ["“read relaxed", "energies from", "VASP OUTCAR", "files”"]
DESC_N = ["“read relaxed", "energies from VASP", "OUTCAR files”"]
SOURCES = ["registry", "PyPI", "GitHub"]
LIBS = [("pymatgen", "REGISTRY", .92), ("ase", "REGISTRY", .81), ("catkit", "GITHUB", .74)]  # merged, ranked by relevance
# (PyPI looks up exact query words only, so this query finds nothing there that ranks; search/pypi.py:30-31)
KW = ("def", "for", "if", "in", "return", "assert", "and")
CODE = [(0, "def read_energies(path):"), (1, "out = []"), (1, "for ln in open(path):"), (2, 'if "sigma->0" in ln:'),
        (3, "e = ln.split()[-1]"), (3, "out.append(float(e))"), (1, "return out")]
TEST = [(0, "def test_read_energies():"), (1, 'e = read_energies("OUTCAR")'), (1, "assert e and e[-1] < 0")]
CHECKS = ["syntax", "imports", "types", "lint", "contract"]
N_DEF = 2  # syntax and imports run by default; types, lint and contract only in strict mode (C43)
ARS = 63
WEIGHTS = [("syntax", ".2", .2), ("imports", ".2", .2), ("tests", ".3", .3), ("lint", ".15", .15), ("types", ".15", .15)]
ISLES, PER_ISLE = 5, 9  # 45 new programs over the 50 iterations shown (illustrative sample)

# --- timing (s, within one pass) --------------------------------------------------------------------------------------
T_BASE, T_CAND, CAND_ST = 0, .45, .03  # candidates appear unscored, on a row of their own
SEG = [(.8, .9), (2.2, .9), (3.6, .9)]  # stage progress: start, duration
MV_D = .4
MV = [a + d for a, d in SEG]  # a stage's scores land only when that stage has finished
T_D1, T_D2 = MV[0] + MV_D + .05, MV[1] + MV_D + .05  # then its decision: the dropped fade, the holdout picks turn teal
T_HB, T_MARG = SEG[2][0], SEG[2][0] + .4  # holdout starts: the baseline line moves to its holdout mean, the band shows
T_CI = MV[2] + MV_D + .05  # CIs after the holdout scores have landed
T_HALO, T_WAIT, T_OK, T_ACT = T_CI + .5, T_CI + .8, T_CI + 1.9, T_CI + 2.2
DIM = .18  # dropped candidates fade this far
T_SRC = [.2, .35, .5]
T_LIB = [.8, .95, 1.1]
T_TYPE, LINE_D, LINE_GAP = 1.4, .2, .03
N_LINES = len(CODE) + len(TEST)
T_CHK = T_TYPE + N_LINES * (LINE_D + LINE_GAP) + .15
CHK_ST = .22
T_RUN = T_CHK + N_DEF * CHK_ST + .1  # the isolated runner works only after inspection passed
T_TESTS = T_RUN + .6
T_STAGED, T_EVT, T_EVS = T_TESTS + .25, T_TESTS + .25, T_TESTS + .45
T_FILL, FILL_D = T_EVS + .3, .7
T_READ = T_FILL + FILL_D + .1
T_IT, IT_D = .2, 6.0
T_BEST = T_IT + IT_D + .15
PASS = max(T_READ, T_ACT, T_BEST) + .35
T0_INTRO, HOLD_T, T0_LOOP = 1.3, 1.5, 2.2
T_LOOP = T0_LOOP + PASS + .1
assert T0_INTRO + PASS <= 10 and T_LOOP <= 10, (PASS, T_LOOP)
assert T_CAND > T_BASE and T_CAND + 11 * CAND_ST < MV[0] and T_D1 < SEG[1][0] and T_D2 <= T_HB and T_CI > MV[2] + MV_D
assert T_CHK > T_TYPE + N_LINES * (LINE_D + LINE_GAP) and T_TYPE > max(T_LIB)


def _tv(t):
    return f"{t:.2f}".rstrip("0").rstrip(".")


def _txt(cls, x, y, s, anchor="start", attrs=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    b = f" {attrs}" if attrs else ""
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}"{a}{b}>{escape(s)}</text>'


def _at(e, t, extra=""):
    """Reveal attributes: data-e names the event (tests check its order), data-t the reveal time within a pass."""
    return f'data-e="{e}" data-t="{_tv(t)}"' + (f" {extra}" if extra else "")


def _tick(cx, cy, r, cls, attrs):
    """A passed-check badge: circle and tick (the tick draws in)."""
    k = r / 9
    return (f'<g class="{cls}" {attrs}><circle cx="{f(cx)}" cy="{f(cy)}" r="{r}"/>'
            f'<path class="f-improvement-dr" d="M{f(cx - 4 * k)},{f(cy + .5 * k)} l{f(3 * k)},{f(3 * k)} l{f(5 * k)},{f(-6 * k)}"/></g>')


def _defs(pre):
    return (f'<defs><linearGradient id="{pre}-pnl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="f-improvement-g0"/>'
            f'<stop offset="1" class="f-improvement-g1"/></linearGradient></defs>')


def _pl(x, y, s):
    return f'<text class="f-improvement-pl" x="{x}" y="{y}">{s}</text>'


# --- (a) components --------------------------------------------------------------------------------------------------
def _plot(v, x0, y0, x1, y1, cx, win_lbl, clabels):
    """Plot frame, grid, baseline (select -> holdout), margin band, 12 candidates, holdout CIs, the verdict."""
    k = (y1 - y0) / .5
    Y = lambda s: y1 - (s - .4) * k
    cw, lw = CW[v], LBL[v]
    P = [f'<rect class="f-improvement-plot" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="6"/>']
    gx = x1 - 6 - max(len(s) for s in ("select mean", "holdout mean", "+ margin")) * lw - 8  # grid stops before the labels
    for s in (.5, .6, .7, .8):
        P.append(f'<path class="f-improvement-grid" d="M{x0},{f(Y(s))} H{f(gx)}"/>' + _txt("sub", x0 - 5, Y(s) + 4.5, f"{s:.1f}", "end"))
    ax = x0 - (42 if v == "wide" else 36)
    P.append(_txt("sub", ax, (y0 + y1) / 2, "score", "middle", f'transform="rotate(-90 {f(ax)} {f((y0 + y1) / 2)})"'))
    # margin band and baseline: the line sits at the holdout mean; the pass starts it at the select mean
    P.append(f'<rect class="f-improvement-band" x="{x0}" y="{f(Y(BASE_HOLD + MARGIN))}" width="{x1 - x0}" '
             f'height="{f(Y(BASE_HOLD) - Y(BASE_HOLD + MARGIN))}" {_at("marg", T_MARG)}/>')
    P.append(f'<path class="f-improvement-bl" d="M{x0},{f(Y(BASE_HOLD))} H{x1}" {_at("base", T_BASE)} '
             f'data-hb="{f(Y(BASE_SEL) - Y(BASE_HOLD))}"/>')
    xr = x1 - 6
    labs = [("select mean", Y(BASE_SEL) - 6, f'data-w="0 {_tv(T_HB)}" opacity="0"'),  # hidden in the finished frame
            ("holdout mean", Y(BASE_HOLD) + 16, _at("hbl", T_MARG)), ("+ margin", Y(BASE_HOLD + MARGIN) - 6, _at("mlbl", T_MARG))]
    for s, y, a in labs:
        P.append(_txt("lbl amb", xr, y, s, "end", a))
    yu = y1 - (14 if v == "wide" else 12)  # the unscored row
    P.append(_txt("lbl", xr, yu + 4, "unscored", "end", f'data-w="{_tv(T_CAND)} {_tv(MV[0] + .2)}" opacity="0"'))
    zone = xr - max(len(s) for s, _y, _a in labs) * lw
    assert cx(11) + 6 + 6 <= zone, (cx(11), zone)
    for i in range(12):
        x, yf = cx(i), Y(FINAL[i])
        y_1 = Y(S1[i]) - yf
        y_2 = (Y(S2[i]) - yf) if i in S2 else y_1
        dim = {0: T_D1, 1: T_D2}.get(KIND[i])
        P.append(f'<g class="f-improvement-cand" data-k="{KIND[i]}" {_at("cand", T_CAND + i * CAND_ST)} '
                 f'data-y="{f(yu - yf)} {f(y_1)} {f(y_2)}" data-mv="{" ".join(_tv(m) for m in MV)}"'
                 + (f' data-dim="{_tv(dim)}" opacity="{DIM}"' if dim else "") + '>'
                 f'<circle class="f-improvement-dot" cx="{f(x)}" cy="{f(yf)}" r="{6 if v == "wide" else 5}"/>'
                 + (f'<circle class="f-improvement-on" cx="{f(x)}" cy="{f(yf)}" r="{6 if v == "wide" else 5}" {_at("on", T_D2)}/>'
                    if KIND[i] == 2 else "") + '</g>')
        if KIND[i] == 2:
            m, lo, hi = HOLD[i]
            ok = i in WIN
            P.append(f'<path class="f-improvement-ci{" ok" if ok else ""}" d="M{f(x)},{f(Y(lo))} V{f(Y(hi))} M{f(x - 7)},{f(Y(lo))} h14 '
                     f'M{f(x - 7)},{f(Y(hi))} h14" {_at("ci", T_CI)} data-o="{f(x)} {f(yf)}"/>')
            if ok:
                P.append(f'<circle class="f-improvement-halo" cx="{f(x)}" cy="{f(Y(lo))}" r="10" {_at("halo", T_HALO)}/>')
                s = "CI lower bound clears"
                lx, ly = x + win_lbl, Y(hi) - 6
                assert lx + len(s) * OKW[v] <= x1 - 4 and ly - 12 > y0 and ly + 4 < Y(.8) - 2, (lx, ly)
                P.append(_txt("lbl ok", lx, ly, s, attrs=_at("verdict", T_HALO)))
        if clabels == "all":
            P.append(_txt("sub", x, y1 + 20, f"c{i + 1}", "middle"))
        elif KIND[i] == 2:  # narrow: only the holdout candidates are named, once they are chosen
            P.append(_txt("sub", x, y1 + 20, f"c{i + 1}", "middle", _at("on", T_D2)))
    return "".join(P)


def _track(v, x0, x1, y, tags_y):
    """Stage progress: three thirds that fill in turn; wide shows the three tags, narrow one caption that changes."""
    w = (x1 - x0) / 3
    P = [f'<path class="f-improvement-trk" d="M{x0},{y} H{x1}"/>']
    tags = [f"1 · 20{NB}% SUBSET", "2 · SELECT SPLIT", "3 · HOLDOUT"]
    for j, (t0, d) in enumerate(SEG):
        a, b = x0 + j * w + (2 if j else 0), x0 + (j + 1) * w - (2 if j < 2 else 0)
        P.append(f'<path class="f-improvement-prog f-improvement-draw" d="M{f(a)},{y} H{f(b)}" {_at("seg", t0)} data-dd="{_tv(d)}"/>')
        if tags_y is not None:
            assert len(tags[j]) * TW[v] <= w - 8
            P.append(_txt("tag", x0 + (j + .5) * w, tags_y, tags[j], "middle"))
    if tags_y is None:
        on = [0, SEG[1][0], SEG[2][0]]
        for j, s in enumerate(tags):
            s = "STAGE " + s
            assert len(s) * TW[v] <= x1 - 12
            w_ = f'data-w="{_tv(on[j])} {_tv(on[j + 1] - .2)}"' if j < 2 else f'data-w="{_tv(on[j])}"'
            P.append(_txt("tag", 12, y + 24, s, attrs=w_ + ("" if j == 2 else ' opacity="0"')))
    return "".join(P)


def _ladder(v, x, y0, w, h, pitch, tag_dx):
    """The path to Active: five steps, each lit in turn; approval waits (amber) and gets a tick before Active lights."""
    P, times = [], [T_BASE, T_CAND, T_HB, T_WAIT, T_ACT]
    evs = ["base", "cand", "hold", "wait", "active"]
    for j, (t, s, k) in enumerate(STEPS):
        y = y0 + j * pitch
        assert len(t) * 14.5 * .58 + 16 + 30 <= w and len(s) * CW[v] + 16 + (30 if j == 3 else 0) <= w, (t, s)
        P.append(f'<g class="card f-improvement-step{(" " + k) if k else ""}"><rect x="{x}" y="{f(y)}" width="{w}" height="{h}" rx="10"/>'
                 + _txt("ttl", x + 16, y + (21 if h < 54 else 24), t) + _txt("sub", x + 16, y + (41 if h < 54 else 44), s)
                 + _txt("tag", x + w - tag_dx, y + 19, f"0{j + 1}", "end") + '</g>')
        if j < 4:
            P.append(curve(x + w / 2, y + h, x + w / 2, y + pitch, vertical=True))
        P.append(f'<rect class="f-improvement-lit{(" " + k) if k == "amb" else ""}" x="{x}" y="{f(y)}" width="{w}" height="{h}" rx="10" '
                 + (_at(evs[j], times[j]) if j != 3 else f'data-e="wait" data-t="{_tv(T_WAIT)}"') + '/>')
    ya = y0 + 3 * pitch
    P.append(f'<rect class="f-improvement-wait" x="{x - 4}" y="{f(ya - 4)}" width="{w + 8}" height="{h + 8}" rx="13" '
             f'data-w="{_tv(T_WAIT)} {_tv(T_OK)}" opacity="0"/>')
    P.append(_tick(x + w - 24, ya + h - 18, 9, "f-improvement-okb", _at("ok", T_OK)))
    return "".join(P), ya


# --- (b) components --------------------------------------------------------------------------------------------------
def _card(x, y, w, h, title, subs, v, cls="", sub_dy=20, attrs=""):
    room = w - 28
    assert len(title) * TTL_SM <= room, title
    P = [f'<g class="card{(" " + cls) if cls else ""}"{(" " + attrs) if attrs else ""}><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="10"/>',
         _txt("ttl sm", x + 14, y + 22, title)]
    for j, s in enumerate(subs):
        assert len(s) * CW[v] <= room and len(s) <= 22, s
        P.append(_txt("sub", x + 14, y + 42 + sub_dy * j, s))
    return "".join(P) + "</g>"


def _pill(x, y, s, t, v):
    """A library source: its name, and a tick once it has been searched."""
    w = 10 + len(s) * CW[v] + 6 + 16 + 6
    return (f'<g class="f-improvement-chip"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="26" rx="13"/>'
            + _txt("sub", x + 10, y + 17.5, s) + '</g>'
            + _tick(x + w - 14, y + 13, 7.5, "f-improvement-okb", _at("src", t))), w


def _libcards(x, y, w, v):
    P = []
    for j, (name, src, rel) in enumerate(LIBS):
        yy = y + j * 42
        bw = (w - 24) * rel
        assert len(name) * TTL_SM + len(src) * TW[v] + 40 <= w
        P.append(f'<g class="card f-improvement-lib" {_at("lib", T_LIB[j])}><rect x="{f(x)}" y="{f(yy)}" width="{f(w)}" height="36" rx="8"/>'
                 + _txt("ttl sm", x + 12, yy + 17, name) + _txt("tag", x + w - 12, yy + 17, src, "end")
                 + f'<path class="f-improvement-bar f-improvement-dr" d="M{f(x + 12)},{f(yy + 27)} h{f(bw)}"/></g>')
    return "".join(P)


def _code(x_num, x, y, pitch, lines, n0, cw, pre):
    """Code lines, each typed in through its own clip wipe (steps, one per character); keywords bold."""
    P = []
    for j, (ind, s) in enumerate(lines):
        n = n0 + j
        yy = y + j * pitch
        cx = x + ind * 4 * cw
        t = T_TYPE + n * (LINE_D + LINE_GAP)
        parts = []
        for tok in s.split(" "):
            parts.append(f'<tspan class="f-improvement-kw">{tok}</tspan>' if tok in KW else escape(tok))
        P.append(f'<clipPath id="{pre}-l{n}"><rect class="f-improvement-wipe" x="{f(cx - 1)}" y="{f(yy - 13)}" '
                 f'width="{f(len(s) * cw + 2)}" height="18" data-ty="{_tv(t)}" data-n="{len(s)}" '
                 f'data-c="{f(cx)} {f(yy - 12)}"' + (f' {_at("code", t + LINE_D)}' if n == N_LINES - 1 else "") + '/></clipPath>'
                 + _txt("sub f-improvement-pm", x_num, yy, str(n + 1), "end")
                 + f'<text class="f-improvement-code" x="{f(cx)}" y="{f(yy)}" clip-path="url(#{pre}-l{n})">{" ".join(parts)}</text>')
    return "".join(P)


def _checks(pos, strict_at):
    """Inspection checks on the panel: syntax and imports ticked in order; types, lint and contract under "strict mode"
    with dashed badges, never ticked (strict validation is off by default, C43)."""
    P = [_txt("sub f-improvement-pm", *strict_at, "strict mode")]
    for j, (s, (x, y)) in enumerate(zip(CHECKS, pos)):
        P.append(f'<circle class="f-improvement-bdg{"" if j < N_DEF else " sd"}" cx="{f(x + 7)}" cy="{f(y - 4.5)}" r="7"/>'
                 + _txt("sub f-improvement-pi" if j < N_DEF else "sub f-improvement-pm", x + 21, y, s)
                 + (_tick(x + 7, y - 4.5, 7, "f-improvement-ck", _at("chk", T_CHK + j * CHK_ST)) if j < N_DEF else ""))
    return "".join(P)


def _runner(x, y, w, h, v, sub_x, sub_dy):
    """The isolated runner: only after inspection passed do the module's own tests run in it."""
    assert len("ISOLATED RUNNER") * TW[v] + 12 <= w
    ty = y + 40
    return (f'<rect class="f-improvement-run" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="8"/>'
            f'<rect class="f-improvement-runw" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="8" '
            f'data-w="{_tv(T_RUN)} {_tv(T_TESTS)}" opacity="0"/>'
            + _txt("tag f-improvement-pm", x + 8, y + 20, "ISOLATED RUNNER")
            + f'<circle class="f-improvement-bdg" cx="{f(x + 17)}" cy="{f(ty - 4.5)}" r="7"/>'
            + _txt("sub f-improvement-pi", x + 31, ty, "tests")
            + _tick(x + 17, ty - 4.5, 7, "f-improvement-ck", _at("tests", T_TESTS))
            + _txt("sub f-improvement-pm", sub_x, ty + sub_dy[0], "macOS sandbox-exec")
            + _txt("sub f-improvement-pm", sub_x, ty + sub_dy[1], "or a container"))


def _staging(x, y, w, v):
    """Staging card: the module lands only once the checks pass (C70)."""
    cw = 13 * CW[v] + 18
    assert cw <= w - 16
    return (_card(x, y, w, 76, "Staging", ["if checks pass"], v, "dashed", 19)
            + f'<g class="f-improvement-mod" {_at("staged", T_STAGED)}><rect x="{f(x + 8)}" y="{f(y + 50)}" width="{f(w - 16)}" height="20" rx="6"/>'
            + _txt("sub", x + 17, y + 64.5, "energy_reader") + "</g>")


def _ready(x, y, w, v, read_x):
    """Readiness (ARS, C67): evidence chips first, then the bar fills, then the readout."""
    assert len("READINESS · ARS") * TW[v] <= w
    P = [_txt("tag", x, y, "READINESS · ARS")]
    cx = x
    for s, e, t in (("tests", "evid", T_EVT), ("security", "evid2", T_EVS)):
        cw = 19 + len(s) * CW[v] + 6
        P.append(f'<g class="f-improvement-ev" {_at(e, t)}><rect x="{f(cx)}" y="{f(y + 10)}" width="{f(cw)}" height="20" rx="10"/>'
                 f'<path class="f-improvement-evt f-improvement-dr" d="M{f(cx + 6)},{f(y + 20)} l3,3 l5,-6"/>'
                 + _txt("sub", cx + 19, y + 24.5, s) + "</g>")
        cx += cw + 4
    assert cx - 4 <= x + w, cx
    mw = read_x - 30 - x
    my = y + 42
    P.append(f'<rect class="f-improvement-mtr" x="{f(x)}" y="{f(my)}" width="{f(mw)}" height="12" rx="3"/>'
             f'<rect class="f-improvement-fill" x="{f(x)}" y="{f(my)}" width="{f(mw * ARS / 100)}" height="12" rx="3" '
             f'{_at("fill", T_FILL)} data-ty="{_tv(T_FILL)}" data-dd="{_tv(FILL_D)}"/>')
    P.append(f'<path class="f-improvement-cells" d="{" ".join(f"M{f(x + mw * k / 10)},{f(my)} v12" for k in range(1, 10))}"/>')
    P.append(f'<text class="f-improvement-read" x="{f(read_x)}" y="{f(my + 12)}" text-anchor="end" {_at("read", T_READ)}>{ARS}</text>')
    P.append(_txt("sub", x, my + 32, "only with both"))
    return "".join(P)


def _fitness(x, y, w, v):
    """OpenEvolve's fitness: the five weighted checks (C71) as a proportional bar, weights inside, names under."""
    P, cx = [_txt("tag", x, y, "FITNESS")], x
    for j, (s, wt, share) in enumerate(WEIGHTS):
        sw = w * share
        assert len(s) * CW[v] <= sw - 4, s
        P.append(f'<rect class="f-improvement-wt k{j}" x="{f(cx)}" y="{f(y + 8)}" width="{f(sw - 2)}" height="22" rx="4"/>'
                 + _txt("sub f-improvement-wtt", cx + sw / 2 - 1, y + 23.5, wt, "middle")
                 + _txt("sub", cx + sw / 2 - 1, y + 48, s, "middle"))
        cx += sw
    return "".join(P)


def _iters(x, y, w):
    return (_txt("tag", x, y, "ITERATIONS") + f'<path class="f-improvement-trk" d="M{x},{y + 12} H{x + w}"/>'
            f'<path class="f-improvement-prog f-improvement-draw" d="M{x},{y + 12} H{x + w}" {_at("prog", T_IT)} data-dd="{_tv(IT_D)}"/>'
            + _txt("sub", x, y + 32, "0") + _txt("sub", x + w, y + 32, "50 iterations", "end"))


def _islands(cx, cy, rx, ry, R, v):
    """Five islands on a ring, each a contour map whose summit is the highest fitness; each new program appears as a
    dot placed by its fitness, round-robin across islands over the iterations; the best one is marked last."""
    rnd, rfit = random.Random(7), random.Random(11)  # fitness has its own stream, so both variants agree
    P, dots, best = [], [], None
    centres = [(cx + rx * math.cos(math.radians(-90 + 72 * i)), cy + ry * math.sin(math.radians(-90 + 72 * i))) for i in range(ISLES)]
    for i, (x, y) in enumerate(centres):
        rot = rnd.uniform(-25, 25)
        sx, sy = x + R * .14, y - R * .1  # summit, a little off-centre
        P.append(f'<g class="f-improvement-isle">'
                 f'<ellipse class="c0" cx="{f(x)}" cy="{f(y)}" rx="{f(R)}" ry="{f(R * .8)}" transform="rotate({rot:.0f} {f(x)} {f(y)})"/>'
                 f'<ellipse class="c1" cx="{f((x + sx) / 2)}" cy="{f((y + sy) / 2)}" rx="{f(R * .64)}" ry="{f(R * .5)}" transform="rotate({rot:.0f} {f(x)} {f(y)})"/>'
                 f'<ellipse class="c2" cx="{f(sx)}" cy="{f(sy)}" rx="{f(R * .3)}" ry="{f(R * .24)}" transform="rotate({rot:.0f} {f(x)} {f(y)})"/></g>')
        placed = []
        for j in range(PER_ISLE):
            fit = .97 if (i, j) == (0, PER_ISLE - 1) else min(.95, .42 + .5 * (j / (PER_ISLE - 1)) ** .8 + rfit.uniform(-.05, .05))
            rho = (1 - (fit - .3) / .7) * .95
            for n_ in range(300):  # spread the dots: no two closer than 7.5 units (drift outwards if crowded)
                a, rr = rnd.uniform(0, 2 * math.pi), min(.95, rho + n_ * .002)
                px, py = sx + rr * R * .92 * math.cos(a), sy + rr * R * .72 * math.sin(a)
                if all(math.hypot(px - qx, py - qy) >= 7.5 for qx, qy in placed):
                    break
            else:
                raise AssertionError("cannot place program dot")
            placed.append((px, py))
            k = j * ISLES + i  # iteration order: round-robin over islands
            dots.append((k, px, py, fit))
            if best is None or fit > best[3]:
                best = (k, px, py, fit, i)
    P.append('<g class="f-improvement-p">')  # one class on the group keeps the 45 dots lean
    for k, px, py, fit in sorted(dots):
        t = T_IT + (k + 1) / (ISLES * PER_ISLE) * IT_D - .05
        P.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="3.2" data-t="{_tv(t)}"/>')
    P.append('</g>')
    _k, bx, by, _f, bi = best
    assert bi == 0  # the label sits above the top island
    pts = " ".join(f"{f(bx + (8 if q % 2 == 0 else 3.4) * math.cos(math.radians(-90 + 36 * q)))},"
                   f"{f(by + (8 if q % 2 == 0 else 3.4) * math.sin(math.radians(-90 + 36 * q)))}" for q in range(10))
    P.append(f'<path class="f-improvement-star" d="M{pts} Z" {_at("best", T_BEST)}/>')
    return "".join(P), centres, (bx, by)


def _legend_items():
    return [("dot", "on holdout"), ("hdot", "dropped"), ("amber", "baseline · waiting"), ("okc", "check passed"),
            ("isle", "program"), ("dash", "separate step")]


LABEL = ("Two panels; values are illustrative. (a) An improvement run measures a baseline, then a language model proposes "
         f"12 candidates: prompt, setting, code or workflow edits. Stage 1 scores each on a 20{NB}% subset of the select split "
         "and keeps the top third; stage 2 scores those on the whole select split, and up to three above the baseline's "
         "select mean go on to the holdout split. A candidate goes to review only if the lower bound of its holdout "
         "confidence interval exceeds the baseline's holdout mean plus a margin; here one does. It becomes active only "
         "after an administrator approves it. For DISCOVER's own code-generation program, approval instead writes one "
         "commit on a new local git branch, never pushed; that target runs on macOS only. (b) From a plain-language "
         "description, here a reader for energies in VASP OUTCAR files, DISCOVER first searches a curated registry, PyPI "
         "and GitHub for existing libraries and ranks them by relevance, then writes a module with its tests. Syntax and "
         "import checks run, and type, lint and contract checks too in strict mode, which is off by default; then the "
         "module's own tests run in an isolated runner, macOS sandbox-exec or a container. The checks show that the code "
         "runs and passes its tests, not that it is correct. "
         "Only then are the files written to staging; promotion into the live system is a separate step that needs passed "
         "tests. A readiness score, ARS, 0–100, is reported only when test and security results back it. OpenEvolve, "
         "SE 7.4, which needs an Anthropic API key, evolves code over five island populations for 50 iterations by "
         "default; each dot is a program, placed higher on its island the higher its fitness, which weighs 0.2 syntax, "
         "0.2 imports, 0.3 tests, 0.15 lint and 0.15 types. The best program is recorded in the module catalog.")


# --- layouts ----------------------------------------------------------------------------------------------------------
def _wide():
    W, v, pre = 1100, "wide", "im-w"
    cw = CW[v]
    P = [_defs(pre), _pl(30, 31, "a"), hdr(52, 30, "CANDIDATES AGAINST THE BASELINE"), hdr(690, 30, "PATH TO ACTIVE")]
    x0, y0, x1, y1 = 96, 52, 660, 352
    P.append(_plot(v, x0, y0, x1, y1, lambda i: x0 + 28 + 36 * i, 14, "all"))
    P.append(_track(v, x0, x1, 410, 398))
    lad, ya = _ladder(v, 690, 50, 230, 58, 74, 14)
    P.append(lad)
    gy = ya - 14
    P.append(f'<path class="cv f-improvement-opt" d="M920,{ya + 28} H932" marker-end="url(#arr)"/>')
    P.append(_card(936, gy, 134, 98, "git branch", ["DISCOVER code", "not pushed", "macOS only"], v, "dashed", 18))
    # (b) row 1: description -> library search -> module bench -> staging, readiness
    yb = 470
    P += [_pl(30, yb + 1, "b"), hdr(52, yb, "DESCRIPTION"), hdr(194, yb, "LIBRARY SEARCH"), hdr(416, yb, "GENERATED MODULE · CHECKS"),
          hdr(912, yb, "STAGED · SCORED")]
    P.append(_card(30, 486, 140, 114, "Description", DESC_W, v, sub_dy=18))
    P.append(_txt("tag", 30, 620, "PLAIN LANGUAGE"))
    px = 194
    P.append(curve(170, 543, px - 2, 531))
    for j, (s, t) in enumerate(zip(SOURCES, T_SRC)):
        pill, pw = _pill(px, 486 + 32 * j, s, t, v)
        P.append(pill)
    P.append(curve(210, 578, 210, 606, vertical=True))
    P.append(_txt("lbl", 228, 600, "ranked by relevance"))
    P.append(_libcards(194, 610, 200, v))
    # the module bench: the one dark focal panel
    bx0, bx1, by0, by1 = 416, 894, 484, 750
    P.append(curve(394, 670, bx0 - 2, 640))
    P.append(f'<rect class="panel f-improvement-hous" x="{bx0}" y="{by0}" width="{bx1 - bx0}" height="{by1 - by0}" rx="16" '
             f'style="fill:url(#{pre}-pnl)"/>')
    P.append("".join(f'<circle class="f-improvement-dt" cx="{bx0 + 16 + 12 * k}" cy="{by0 + 16}" r="3.5"/>' for k in range(3)))
    P.append(_txt("sub f-improvement-pi", 472, by0 + 21, "energy_reader.py"))
    P.append(f'<path class="f-improvement-rule" d="M{bx0 + 12},{by0 + 30} H716 M728,{by0 + 8} V{by1 - 8} M{bx0 + 12},662 H716"/>')
    P.append(_code(452, 464, 536, 18.5, CODE, 0, cw, pre))
    P.append(_txt("sub f-improvement-pi", 464, 680, "test_energy_reader.py"))
    P.append(_code(452, 464, 700, 18, TEST, len(CODE), cw, pre))
    assert 464 + max(len(s) + 4 * i for i, s in CODE + TEST) * cw <= 716
    P.append(f'<rect class="f-improvement-caret" x="0" y="0" width="7" height="15" opacity="0"/>')
    P.append(hdr(742, by0 + 22, "CHECKS").replace('class="hdr"', 'class="hdr f-improvement-pm"'))
    P.append(_checks([(742, 530), (742, 553), (742, 600), (742, 621), (742, 642)], (742, 579)))
    P.append(_runner(734, 656, 152, 88, v, 742, (18, 36)))
    # staging, promotion, readiness
    rx, rw = 912, 158
    P.append(_staging(rx, 486, rw, v))
    P.append(f'<path class="cv f-improvement-opt" d="M{rx + rw / 2},562 V588" marker-end="url(#arr)"/>' + _txt("lbl", rx + rw / 2 + 8, 580, "promote"))
    P.append(_card(rx, 592, rw, 54, "Live system", ["tests must pass"], v, "dashed", 19))
    P.append(curve(bx1, 600, rx - 2, 524))
    P.append(curve(bx1, 700, rx - 2, 690))
    P.append(_ready(rx, 668, rw, v, 1070))
    # (b) row 2: OpenEvolve
    P += [hdr(30, 790, "OPENEVOLVE · SE 7.4"), _txt("lbl", 30, 812, "needs an Anthropic API key")]
    P.append(_fitness(30, 844, 350, v))
    P.append(_iters(30, 926, 350))
    P.append(_txt("lbl", 30, 990, "here from a catalogued module"))
    isl, cen, (bx, by) = _islands(740, 902, 250, 64, 54, v)
    P.append(isl)
    P.append(_txt("sub", 740, 774, "best → module catalog", "middle", _at("best", T_BEST)))
    P.append(_txt("lbl", 412, 800, "each dot a program") + _txt("lbl", 1070, 800, "summit = higher fitness", "end"))
    H = 1040
    items = _legend_items()
    P.append(legend(items, 30, H - 18) + note(W - 30 - 23 * cw, H - 18))
    assert 30 + sum(30 + int(len(t) * 8.1) + 22 for _, t in items) < W - 30 - 23 * cw
    return svg(W, H, "".join(P), v, LABEL)


def _narrow():
    W, v, pre = 360, "narrow", "im-n"
    cw = CW[v]
    P = [_defs(pre), _pl(12, 25, "a"), hdr(34, 24, "CANDIDATES VS BASELINE")]
    x0, y0, x1, y1 = 50, 40, 348, 264
    P.append(_plot(v, x0, y0, x1, y1, lambda i: x0 + 16 + 16 * i, 10, "holdout"))
    P.append(_track(v, x0, x1, 296, None))
    P.append(hdr(12, 356, "PATH TO ACTIVE"))
    lad, ya = _ladder(v, 12, 370, 336, 52, 60, 14)
    P.append(lad)
    gy = 370 + 4 * 60 + 52 + 12
    P.append(f'<path class="cv f-improvement-opt" d="M348,{ya + 26} C359,{ya + 26} 359,{gy + 32} 350,{gy + 32}" marker-end="url(#arr)"/>')
    P.append(_card(12, gy, 336, 70, "git branch", ["DISCOVER code only", "local, not pushed"], v, "dashed", 18))
    P.append(_txt("tag", 334, gy + 22, "MACOS ONLY", "end"))
    # (b)
    yb = gy + 70 + 38
    P += [_pl(12, yb + 1, "b"), hdr(34, yb, "NEW MODULE")]
    dy = yb + 14
    P.append(_card(12, dy, 336, 90, "Description", DESC_N, v, sub_dy=18))
    P.append(_txt("tag", 334, dy + 22, "PLAIN LANGUAGE", "end"))
    ly = dy + 90 + 40
    P.append(hdr(12, ly - 2, "LIBRARY SEARCH"))
    px, pills = 12, []
    for j, (s, t) in enumerate(zip(SOURCES, T_SRC)):
        pill, pw = _pill(px, ly + 10, s, t, v)
        pills.append((px, pw))
        P.append(pill)
        px += pw + 8
    assert px - 8 <= W - 12
    gx = pills[2][0] + pills[2][1] / 2
    P.append(curve(290, dy + 90, gx, ly + 8, vertical=True))
    P.append(_txt("lbl", 12, ly + 64, "ranked by relevance"))
    P.append(curve(gx, ly + 36, gx + 30, ly + 72, vertical=True))
    P.append(_libcards(12, ly + 74, 336, v))
    by0 = ly + 74 + 3 * 42 + 22
    P.append(curve(180, by0 - 22, 180, by0 - 2, vertical=True))
    # the bench panel
    cy0 = by0 + 52
    code_end = cy0 + 18 * (len(CODE) - 1)
    th = code_end + 30
    test0 = th + 22
    chk_hdr = test0 + 18 * (len(TEST) - 1) + 38
    chk0 = chk_hdr + 26
    run0 = chk0 + 3 * 24 + 9  # the contract badge (r 7, 4.5 above its baseline) clears the runner by 6.5
    by1 = run0 + 74 + 12
    P.append(f'<rect class="panel f-improvement-hous" x="12" y="{by0}" width="336" height="{by1 - by0}" rx="16" style="fill:url(#{pre}-pnl)"/>')
    P.append("".join(f'<circle class="f-improvement-dt" cx="{28 + 12 * k}" cy="{by0 + 16}" r="3.5"/>' for k in range(3)))
    P.append(_txt("sub f-improvement-pi", 68, by0 + 21, "energy_reader.py"))
    P.append(f'<path class="f-improvement-rule" d="M24,{by0 + 30} H336 M24,{th - 18} H336 M24,{chk_hdr - 22} H336"/>')
    P.append(_code(44, 54, cy0, 18, CODE, 0, cw, pre))
    P.append(_txt("sub f-improvement-pi", 54, th, "test_energy_reader.py"))
    P.append(_code(44, 54, test0, 18, TEST, len(CODE), cw, pre))
    assert 54 + max(len(s) + 4 * i for i, s in CODE + TEST) * cw <= 340
    P.append(f'<rect class="f-improvement-caret" x="0" y="0" width="7.5" height="16" opacity="0"/>')
    P.append(hdr(28, chk_hdr, "CHECKS").replace('class="hdr"', 'class="hdr f-improvement-pm"'))
    P.append(_checks([(28, chk0 + 24), (28, chk0 + 48), (168, chk0 + 24), (168, chk0 + 48), (168, chk0 + 72)], (168, chk0)))
    P.append(_runner(24, run0, 312, 74, v, 168, (0, 18)))
    # staging + live (left), readiness (right)
    sy = by1 + 32
    P.append(curve(120, by1, 94, sy - 2, vertical=True))
    P.append(curve(240, by1, 268, sy + 12, vertical=True))
    P.append(_staging(12, sy, 164, v))
    P.append(f'<path class="cv f-improvement-opt" d="M94,{sy + 76} V{sy + 98}" marker-end="url(#arr)"/>' + _txt("lbl", 102, sy + 92, "promote"))
    P.append(_card(12, sy + 102, 164, 52, "Live system", ["tests must pass"], v, "dashed", 19))
    P.append(_ready(188, sy + 26, 160, v, 348))
    # OpenEvolve
    oy = sy + 102 + 52 + 40
    P += [hdr(12, oy, "OPENEVOLVE · SE 7.4"), _txt("lbl", 12, oy + 22, "needs an Anthropic API key")]
    P.append(_txt("lbl", 12, oy + 42, "here from a catalogued module"))
    P.append(_fitness(12, oy + 72, 336, v))
    P.append(_iters(12, oy + 152, 336))
    ry = oy + 308
    isl, cen, _b = _islands(180, ry, 118, 62, 33, v)
    P.append(_txt("sub", 180, ry - 62 - 33 - 12, "best → module catalog", "middle", _at("best", T_BEST)))
    P.append(isl)
    yl = ry + 62 * .81 + 33 + 22
    P.append(_txt("lbl", 180, yl, "each dot a program;", "middle") + _txt("lbl", 180, yl + 18, "summit = higher fitness", "middle"))
    lg = yl + 52
    items = _legend_items()
    rows = [items[:2], [items[3], items[5]], [items[2]], [items[4]]]
    P.append("".join(legend(r, 12, lg + 26 * k) for k, r in enumerate(rows)) + note(12 + 30 + 57 + 22 + 20, lg + 78))
    return svg(W, round(lg + 78 + 14), "".join(P), v, LABEL)


JS = """MAFig.register("improvement", function (root, variant) {
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var timed = q("[data-t]"), windows = q("[data-w]"), shown = timed.concat(windows);
  var wipes = q("[data-ty]"), draws = q(".f-improvement-draw"), cands = q(".f-improvement-cand");
  var base = root.querySelector(".f-improvement-bl"), caret = root.querySelector(".f-improvement-caret");
  q("[data-o]").forEach(function (e) { gsap.set(e, {svgOrigin: e.getAttribute("data-o")}); });
  // full widths, read before any tween touches them (a fromTo renders its start at once)
  wipes.forEach(function (r) { r._w = +r.getAttribute("width"); });
  // one pass from t0: every item shows only after the step that decides it (data-t, checked at build time).
  // Every key in a fromTo start object is repeated in its end object (a loop wrap drops start-only keys).
  function pass(tl, t0) {
    tl.set(base, {y: +base.getAttribute("data-hb")}, t0).to(base, {y: 0, duration: .4, ease: "power2.inOut"}, t0 + __HB__);
    cands.forEach(function (c) {
      var y = c.getAttribute("data-y").split(" "), k = +c.getAttribute("data-k");
      var mv = c.getAttribute("data-mv").split(" ");  // each stage's scores land when that stage has finished
      tl.set(c, {y: +y[0]}, t0).to(c, {y: +y[1], duration: __MVD__, ease: "power2.inOut"}, t0 + +mv[0]);
      if (k > 0) tl.to(c, {y: +y[2], duration: __MVD__, ease: "power2.inOut"}, t0 + +mv[1]);
      if (k > 1) tl.to(c, {y: 0, duration: __MVD__, ease: "power2.inOut"}, t0 + +mv[2]);
    });
    timed.forEach(function (el) {
      var t = t0 + +el.getAttribute("data-t");
      tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: .3}, t);
      if (el.hasAttribute("data-dim")) tl.to(el, {opacity: __DIM__, duration: .3}, t0 + +el.getAttribute("data-dim"));
      if (el.classList.contains("f-improvement-ci")) tl.fromTo(el, {scaleY: 0}, {scaleY: 1, duration: .45, ease: "power2.out"}, t);
      var dr = el.querySelectorAll(".f-improvement-dr");
      if (dr.length) tl.fromTo(dr, {drawSVG: "0%"}, {drawSVG: "100%", duration: .35}, t + .1);
    });
    draws.forEach(function (el) {
      tl.fromTo(el, {drawSVG: "0%"}, {drawSVG: "100%", duration: +el.getAttribute("data-dd"), ease: "none"}, t0 + +el.getAttribute("data-t"));
    });
    windows.forEach(function (el) {
      el.getAttribute("data-w").split(" ").forEach(function (s, k) {
        if (k === 0) tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: .2}, t0 + +s);
        else tl.to(el, {opacity: k % 2 ? 0 : 1, duration: .2}, t0 + +s);
      });
    });
    // typing: each line's clip widens one character per step while the caret rides its end
    wipes.forEach(function (r) {
      var t = t0 + +r.getAttribute("data-ty"), n = +r.getAttribute("data-n"), d = r.getAttribute("data-dd");
      tl.fromTo(r, {attr: {width: 0}}, {attr: {width: r._w}, duration: d ? +d : __LINED__, ease: n ? "steps(" + n + ")" : "power2.out"}, t);
      if (!n) return;
      var c = r.getAttribute("data-c").split(" ");
      tl.set(caret, {opacity: 1, x: +c[0], y: +c[1]}, t).to(caret, {x: +c[0] + r._w - 2, duration: __LINED__, ease: "steps(" + n + ")"}, t);
    });
    tl.set(caret, {opacity: 0}, t0 + __TYPEEND__);
  }
  var intro = gsap.timeline({defaults: {ease: "power3.out"}});
  intro.from(q(".hdr, .f-improvement-pl, .legend, .f-improvement-plot, .f-improvement-hous, .card:not([data-t]), .f-improvement-chip, .f-improvement-isle, .cv, " +
               ".tag:not([data-w]):not(.card .tag), .sub:not([data-t]):not(.card .sub), .lbl:not([data-t]):not([data-w])"),
             {opacity: 0, duration: .5, stagger: .01}, 0)
    .from(q(".f-improvement-trk"), {drawSVG: "0%", duration: .5, stagger: .03}, .3)
    .from(q(".f-improvement-grid"), {opacity: 0, duration: .5, stagger: .03}, .3)  // dashed: drawSVG would erase the dashes
    .from(q(".f-improvement-wt, .f-improvement-mtr, .f-improvement-dt, .f-improvement-bdg, .f-improvement-run"), {opacity: 0, duration: .4, stagger: .01}, .5)
    .set(shown, {opacity: 0}, 0)
    .set(wipes, {attr: {width: 0}}, 0)
    .set(cands, {y: function (i, c) { return +c.getAttribute("data-y").split(" ")[0]; }}, 0)
    .set(draws, {drawSVG: "0%"}, 0);
  pass(intro, __T0I__);
  // loop: hold the finished frame, clear what the pass reveals (shown, typed lines, drawn bars), run again.
  // immediateRender off: the frame stays until then.
  var loop = gsap.timeline({repeat: -1, defaults: {immediateRender: false}});
  loop.to(shown, {opacity: 0, duration: .4}, __HOLD__)
    .to(wipes, {attr: {width: 0}, duration: .4}, __HOLD__)
    .to(draws, {drawSVG: "0%", duration: .4}, __HOLD__);
  pass(loop, __T0L__);
  loop.set({}, {}, __TL__);
  return {intro: intro, loop: loop};
});"""
for _k, _v in {"__HB__": T_HB, "__MVD__": MV_D, "__DIM__": DIM, "__LINED__": LINE_D,
               "__TYPEEND__": T_TYPE + N_LINES * (LINE_D + LINE_GAP), "__T0I__": T0_INTRO, "__HOLD__": HOLD_T,
               "__T0L__": T0_LOOP, "__TL__": T_LOOP}.items():
    JS = JS.replace(_k, _tv(_v))
assert "__" not in JS


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
