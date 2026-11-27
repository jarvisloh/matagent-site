"""Record figure: one chained run on an oscilloscope (claims C26, C28, C68).
The dark scope (the one focal panel) carries the harness controls you set (C26: database writes, failed-step policy,
partial results, post-run output checks) and a screen on which the run's event trace scrolls past a write head: each
step is a pulse, a checkpoint diamond follows each step, step 2 fails, and under "ask" the trace flat-lines in amber,
paused for human review, until a person approves; then step 2 re-runs (step 1 is kept, not re-run) and step 3 runs.
Each event lights a tick in the stored event stream, and records drop onto a ledger stack beside the scope (C28, C68)
only after their event has passed the head. Times are illustrative."""
import json
import math
from html import escape

from figkit import Figure, curve_d, f, hdr, legend, note, svg, vcurve_d

CW = {"wide": 7.68, "narrow": 8.04}  # Geist Mono advance per character at the sub size
TW = {"wide": 9.22, "narrow": 9.65}  # tag advance (0.6 em + .12 em letter-spacing)
HW = {"wide": 9.73, "narrow": 10.18}  # header advance (0.6 em + .16 em letter-spacing)
LBL_EM = 0.52  # Geist italic advance per em (line labels)
LBL = {"wide": 12.8 * LBL_EM, "narrow": 13.4 * LBL_EM}

# --- the run, in trace units u = 0..100 (the write head is at u = 100 when the run ends) ------------------------------
D = 6.2  # seconds for the trace to scroll u = 0..100 past the write head


def tau(u):
    return u / 100 * D


def _pulse(u0, u1):
    """A step as a square pulse with a little ringing: rises at u0 (step started), falls at u1 (step finished)."""
    return [(u0, 0), (u0 + .5, 1.1), (u0 + 1, .95), (u0 + 1.5, 1), (u1, 1), (u1 + .5, -.1), (u1 + 1, .04), (u1 + 1.5, 0)]


U_FAIL, U_DIP, U_PAUSE, U_RESUME, U_OK = 31, 32.6, 35, 66.5, 67.2
BREAK = (50, 51.5)  # axis break inside the pause: the review takes far longer than the steps
# teal before the pause: start blip, step 1, step 2 rising then failing (glitch, dip below the baseline)
TRACE_A = ([(0, 0), (2, 0), (2.6, .32), (3.2, 0)] + _pulse(8, 19)
           + [(23, 0), (23.5, 1.1), (24, .95), (24.5, 1), (U_FAIL, 1), (31.4, .62), (31.8, .86), (32.2, .5), (U_DIP, -.4),
              (33.6, -.08), (34.3, .03), (U_PAUSE, 0)])
# teal after the approval blip: step 2 re-runs, step 3, then the run completes
TRACE_B = [(U_RESUME, 0), (U_OK, .32), (67.9, 0)] + _pulse(72, 83) + _pulse(87, 95) + [(100, 0)]
WAVE = TRACE_A + TRACE_B  # the pen follows these vertices (flat at 0 through the pause)
assert all(b[0] > a[0] for a, b in zip(WAVE, WAVE[1:]))
CHECKPOINTS = [21.2, 35.8, 85.2, 97.2]  # after step 1, after step 2 failed (and the pause), after the re-run, after step 3
# (u, amber): run started, step 1 started/finished, step 2 started/failed, awaiting review, approved, step 2 started/
# finished (re-run), step 3 started/finished, run complete; each is one event in the stored event stream
EVENTS = [(2.6, 0), (8, 0), (19, 0), (23, 0), (U_FAIL, 1), (U_PAUSE, 1), (U_OK, 0), (72, 0), (83, 0), (87, 0), (95, 0),
          (100, 0)]
# the run record's slips (C28, C68): (record, details in turn). A run keeps ONE checkpoint and each save replaces it,
# so the checkpoint slip lands once and its detail is rewritten in place; the failed result (amber) is dropped on
# approval and survives in the event stream, not in the checkpoint.
SLIPS = [("INPUT", ("secrets redacted",)),
         ("CHECKPOINT", ("after step 1", "step 2 failed", "after step 2", "after step 3")),
         ("OUTPUTS · METRICS", ()), ("TRACE", ())]
CK_AMBER = 1  # the checkpoint detail that holds the failed result
# (event u, slip): every write to the record, in order; one flow along the connector each
WRITES = [(2.6, 0)] + [(u, 1) for u in CHECKPOINTS] + [(100, 2), (100, 3)]
# (text, event u, band, anchor, anchor u): screen labels (wide bands; narrow puts them all in the label column)
LABELS = [("run starts", 2.6, "low", "start", .4), ("step 1", 8, "top", "middle", 13.5),
          ("step 2", 23, "top", "middle", 27), ("step 2 fails", U_FAIL, "low", "middle", U_DIP),
          ("approved", U_OK, "low", "middle", U_OK), ("step 2 re-runs", 72, "top", "middle", 77.5),
          ("step 3", 87, "top", "middle", 91), ("run complete", 100, "low", "end", 99.4)]
ASK = "ask · paused for human review"
ASK_N = ("ask · paused for", "human review")
TIMES = [("10:02", 2.6), ("10:09", U_PAUSE), ("12:31", U_OK), ("12:40", 100)]  # illustrative clock times

# --- timing (s) ---------------------------------------------------------------------------------------------------
REVEAL = .05  # a label shows just after it has fully passed the write head
FLOW_D, DROP_D, SLIP_GAP = .3, .55, .25  # a record flows to the ledger, then drops onto the stack
FLOW_AT = []  # write index -> flow start (s, within a pass); writes at the same event follow each other
for _j, (_u, _s) in enumerate(WRITES):
    FLOW_AT.append(tau(_u) + REVEAL + (SLIP_GAP if _j and WRITES[_j - 1][0] == _u else 0))
ARRIVE = [t + FLOW_D for t in FLOW_AT]  # the write reaches the ledger
SWAP = .15  # a rewritten detail fades in this long after the old one has started fading out
PASS = max(ARRIVE) + DROP_D
W_RUN = [0, tau(U_PAUSE), tau(U_OK), tau(100)]  # status "running" windows (on, off, on, off)
W_PAUSE = [tau(U_PAUSE), tau(U_OK)]
W_DONE = [tau(100)]
W_RING = [tau(31.4), tau(U_OK)]  # the "ask" setting glows from the failure until the approval
W_PEN_T = [0, tau(U_PAUSE), tau(U_RESUME)]
W_PEN_A = [tau(U_PAUSE), tau(U_RESUME)]
T0_INTRO, HOLD, T0_LOOP = 1.3, 1.3, 2.4
T_LOOP = T0_LOOP + PASS + .1
assert T0_INTRO + PASS <= 10 and T_LOOP <= 10, (T0_INTRO + PASS, T_LOOP)
assert tau(U_OK) < tau(72)  # the approval reaches the head before the re-run starts


def _tv(t):
    return f"{t:.2f}".rstrip("0").rstrip(".")


def _w(ts):
    return " ".join(_tv(t) for t in ts)


def _txt(cls, x, y, s, anchor="start", attrs=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    b = f" {attrs}" if attrs else ""
    return f'<text class="{cls}" x="{f(x)}" y="{f(y)}"{a}{b}>{escape(s)}</text>'


def _timed(cls, x, y, s, u, t, anchor="start"):
    assert t >= tau(u) - 1e-9, (s, u, t)
    return _txt(cls, x, y, s, anchor, f'data-u="{_tv(u)}" data-t="{_tv(t)}"')


# --- geometry per variant -------------------------------------------------------------------------------------------
class _Geo:
    """Maps trace coordinates (u along time, a amplitude) onto a variant: wide runs time left to right with amplitude
    up; narrow runs time top to bottom with amplitude to the right."""

    def __init__(self, v, t0, k, base, amp):
        self.v, self.t0, self.k, self.base, self.amp = v, t0, k, base, amp

    def p(self, u, a=0.0):
        s = self.t0 + u * self.k
        return (s, self.base - a * self.amp) if self.v == "wide" else (self.base + a * self.amp, s)

    def path(self, pts):
        return "M" + " L".join(f"{f(x)},{f(y)}" for x, y in (self.p(u, a) for u, a in pts))


def _trace(g, v):
    """The scrolled layer: trace (teal, with glow), the amber flat-line with its axis break, cursors and bracket of the
    pause, failure and approval badges, checkpoint diamonds, the time axis, labels and timestamps."""
    P = []
    for pts in (TRACE_A, TRACE_B):
        d = g.path(pts)
        P.append(f'<path class="f-record-glow" d="{d}"/><path class="f-record-tr" d="{d}"/>')
    flat = g.path([(U_PAUSE, 0), (BREAK[0], 0)]) + " " + g.path([(BREAK[1], 0), (U_RESUME, 0)])
    P.append(f'<path class="f-record-flat" d="{flat}"/>')
    P.append(_slashes(g, 0))
    # the pause: dashed amber cursors across the grid band
    lo, hi = (-.52, 1.18)
    for u in (U_PAUSE, U_RESUME):
        P.append(f'<path class="f-record-cur" d="{g.path([(u, lo), (u, hi)])}"/>')
    # failure badge at the dip, approval badge above its blip, checkpoint diamonds on the baseline
    x, y = g.p(U_DIP, -.4)
    r = 8 if v == "wide" else 7
    P.append(f'<g class="f-record-xb"><circle cx="{f(x)}" cy="{f(y)}" r="{r}"/>'
             f'<path d="M{f(x - 3)},{f(y - 3)} l6,6 M{f(x + 3)},{f(y - 3)} l-6,6"/></g>')
    x, y = g.p(U_OK, .62 if v == "wide" else .6)
    P.append(f'<g class="f-record-okb"><circle cx="{f(x)}" cy="{f(y)}" r="9"/>'
             f'<path d="M{f(x - 4)},{f(y + .5)} l3,3 l5,-6"/></g>')
    for u in CHECKPOINTS:
        x, y = g.p(u)
        P.append(f'<path class="f-record-cp" d="M{f(x)},{f(y - 5.5)} l5.5,5.5 l-5.5,5.5 l-5.5,-5.5 z"/>')
    return P


def _slashes(g, a, cls="f-record-brk"):
    """Two short slashes marking the axis break at amplitude a."""
    out = []
    for u in BREAK:
        x, y = g.p(u, a)
        out.append(f"M{f(x - 3)},{f(y + 5)} L{f(x + 3)},{f(y - 5)}" if g.v == "wide" else f"M{f(x - 5)},{f(y + 3)} L{f(x + 5)},{f(y - 3)}")
    return f'<path class="{cls}" d="{" ".join(out)}"/>'


def _knob(cx, cy, r, opts, sel, title, v):
    """A rotary selector: options at left, top and right; the pointer turns from the first option to the setting."""
    cw = CW[v]
    off = r + 8
    P = [f'<g class="f-record-knob"><circle class="f-record-kr" cx="{f(cx)}" cy="{f(cy)}" r="{r}"/>']
    for j in range(24):  # knurl
        a = math.radians(j * 15)
        P.append(f'<path class="f-record-kn" d="M{f(cx + (r - 4) * math.cos(a))},{f(cy + (r - 4) * math.sin(a))} '
                 f'L{f(cx + r * math.cos(a))},{f(cy + r * math.sin(a))}"/>')
    P.append(f'<circle class="f-record-kc" cx="{f(cx)}" cy="{f(cy)}" r="{r - 6}"/></g>')
    pos = [(cx - off, cy + 5, "end"), (cx, cy - off - 2, "middle"), (cx + off, cy + 5, "start")]
    for j, (o, (x, y, an)) in enumerate(zip(opts, pos)):
        cls = "sub f-record-pi f-record-on" if j == sel else "sub f-record-pm"
        P.append(_txt(cls, x, y, o, an))
    # pointer drawn at the setting; data-a: degrees back to the first option (the intro turns it from there)
    ang = {0: 180, 1: 270, 2: 0}[sel]
    a = math.radians(ang)
    P.append(f'<path class="f-record-kp" d="M{f(cx)},{f(cy)} L{f(cx + (r - 3) * math.cos(a))},{f(cy + (r - 3) * math.sin(a))}" '
             f'data-a="{(ang - 180) % 360}" data-o="{f(cx)} {f(cy)}"/>')
    P.append(f'<circle class="f-record-kd" cx="{f(cx)}" cy="{f(cy)}" r="2.6"/>')
    P.append(_txt("hdr f-record-pm", cx, cy + r + 24, title, "middle"))
    half_title = len(title) * HW[v] / 2
    left = max(len(opts[0]) * cw + off, half_title)  # extent left of the centre: left option or title
    right = max(len(opts[2]) * cw + off, half_title)
    return "".join(P), (cx - left, cx + right)


def _ring(cx, cy, r, s, v):
    """Amber ring around the top option (the "ask" setting) while the run waits for review."""
    w = len(s) * CW[v] + 14
    y = cy - (r + 10) - 12
    return f'<rect class="f-record-ring" x="{f(cx - w / 2)}" y="{f(y)}" width="{f(w)}" height="18" rx="9" data-w="{_w(W_RING)}" opacity="0"/>'


def _switch(x, cy, ty, title, v):
    P = [f'<rect class="f-record-sw" x="{f(x)}" y="{f(cy - 10)}" width="40" height="20" rx="10"/>',
         f'<circle class="f-record-swk" cx="{f(x + 30)}" cy="{f(cy)}" r="7"/>',
         _txt("sub f-record-pi f-record-on", x + 50, cy + 4.5, "keep"),
         _txt("hdr f-record-pm", x, ty, title)]
    return "".join(P), x + max(50 + 4 * CW[v], len(title) * HW[v])


CHECKS = [("schema", 1), ("result count", 1), ("keywords", 0), ("thresholds", 0), ("latency", 1)]  # illustrative on/off


def _box(x, y, on, s):
    """A check setting: a box (ticked when on) and its name; y is the text baseline."""
    b = (f'<rect class="f-record-cb{" on" if on else ""}" x="{f(x)}" y="{f(y - 10)}" width="11" height="11" rx="2.5"/>'
         + (f'<path class="f-record-cbt" d="M{f(x + 2.5)},{f(y - 4.5)} l2.5,2.5 l4,-5"/>' if on else ""))
    return b + _txt("sub f-record-pi" if on else "sub f-record-pm", x + 17, y, s)


def _status(x, y, v):
    """Bezel status: lamp plus running / paused for review / complete; each text fades in .2 s after the previous one
    has faded out, so two never show at once."""
    on = lambda ts: [t + (.2 if k % 2 == 0 and t > 0 else 0) for k, t in enumerate(ts)]
    return (f'<circle class="f-record-lamp" cx="{f(x)}" cy="{f(y - 4.5)}" r="4.5" data-w="{_w(W_RUN[:3])}"/>'
            f'<circle class="f-record-lamp amb" cx="{f(x)}" cy="{f(y - 4.5)}" r="4.5" data-w="{_w(W_PAUSE)}" opacity="0"/>'
            + _txt("sub f-record-pi f-record-st", x + 11, y, "running", attrs=f'data-w="{_w(on(W_RUN))}" opacity="0"')
            + _txt("sub f-record-pi f-record-st", x + 11, y, "paused for review", attrs=f'data-w="{_w(on(W_PAUSE))}" opacity="0"')
            + _txt("sub f-record-pi f-record-st", x + 11, y, "complete", attrs=f'data-w="{_w(on(W_DONE))}"'))


def _pen(x, y):
    return (f'<g transform="translate({f(x)},{f(y)})"><g class="f-record-pen">'
            f'<circle class="f-record-ping" r="5" opacity="0"/>'
            f'<circle class="f-record-pt" r="4.5" data-w="{_w(W_PEN_T)}"/>'
            f'<circle class="f-record-pa" r="4.5" data-w="{_w(W_PEN_A)}" opacity="0"/></g></g>')


def _ledger(x0, x1, y0, v, inlet):
    """The run record: a stack of slips (first at the bottom) under the inlet, the event-stream ticks, run actions."""
    sh, pitch = (28, 34) if v == "wide" else (30, 36)
    top = y0 + 20  # the top slip's slot
    start = top - 10  # a slip appears here, level with the inlet, then drops to its slot
    P, flows = [], []
    for i, (k, dets) in enumerate(SLIPS):
        y = top + (len(SLIPS) - 1 - i) * pitch
        js = [j for j, (_u, si) in enumerate(WRITES) if si == i]  # this slip's writes
        u, t = WRITES[js[0]][0], ARRIVE[js[0]]
        assert t > tau(u)
        tag_w = len(k) * TW[v]
        assert all(14 + tag_w + 12 + len(d) * CW[v] + 10 <= x1 - x0 - 20 for d in dets), (k, dets)
        sp = f'M{f(x0 + 10)},{f(y + 5)} v{sh - 10}'
        D_ = [f'<g class="f-record-slip" data-u="{_tv(u)}" data-t="{_tv(t)}" data-dy="{f(y - start)}">'
              f'<rect x="{f(x0 + 10)}" y="{f(y)}" width="{f(x1 - x0 - 20)}" height="{sh}" rx="5"/>'
              f'<path class="f-record-sp" d="{sp}"/>', _txt("tag f-record-k", x0 + 24, y + sh / 2 + 4.5, k)]
        for n, (d, j) in enumerate(zip(dets, js)):
            if len(dets) == 1:
                D_.append(_txt("sub", x0 + 24 + tag_w + 12, y + sh / 2 + 4.5, d))
                continue
            # rewritten in place: each detail shows from its write's arrival until the next write replaces it
            on = ARRIVE[j] + (SWAP if n else 0)
            w = [on] + ([ARRIVE[js[n + 1]]] if n + 1 < len(js) else [])
            assert on > tau(WRITES[j][0])
            last = n + 1 == len(dets)
            D_.append(_txt("sub f-record-det", x0 + 24 + tag_w + 12, y + sh / 2 + 4.5, d,
                           attrs=f'data-u="{_tv(WRITES[j][0])}" data-w="{_w(w)}"' + ("" if last else ' opacity="0"')))
            if n == CK_AMBER:  # amber stripe while the checkpoint holds the failed result
                D_.insert(2, f'<path class="f-record-sp amb" d="{sp}" data-u="{_tv(WRITES[j][0])}" data-w="{_w(w)}" opacity="0"/>')
        P.append("".join(D_) + "</g>")
    for j in range(len(WRITES)):
        flows.append(f'<path class="f-record-flow" d="{inlet}" data-f="{_tv(FLOW_AT[j])}" opacity="0"/>')
    yb = top + len(SLIPS) * pitch  # below the bottom slip
    P.append(f'<path class="f-record-rule" d="M{f(x0 + 10)},{f(yb + 6)} H{f(x1 - 10)}"/>')
    ys = yb + 28
    P.append(_txt("tag f-record-lt", x0 + 12, ys, "EVENT STREAM"))
    tx = x0 + 12
    ty = ys + 10
    for j, (u, amb) in enumerate(EVENTS):
        x = tx + j * 17
        P.append(f'<rect class="f-record-tick" x="{f(x)}" y="{f(ty)}" width="10" height="16" rx="2"/>'
                 f'<rect class="f-record-tick on{" amb" if amb else ""}" x="{f(x)}" y="{f(ty)}" width="10" height="16" rx="2" '
                 f'data-u="{_tv(u)}" data-t="{_tv(tau(u) + REVEAL)}"/>')
    assert tx + len(EVENTS) * 17 <= x1 - 10
    yr = ty + 30
    P.append(f'<path class="f-record-rule" d="M{f(x0 + 10)},{f(yr)} H{f(x1 - 10)}"/>')
    P.append(_txt("tag f-record-lt", x0 + 12, yr + 22, "RUN ACTIONS"))
    cx, cy = x0 + 12, yr + 32
    rows = [["pause", "resume", "cancel"], ["replay", "report"]]
    for row in rows:
        cx = x0 + 12
        for s in row:
            w = len(s) * CW[v] + 18
            P.append(f'<g class="f-record-chip"><rect x="{f(cx)}" y="{f(cy)}" width="{f(w)}" height="22" rx="11"/>'
                     + _txt("sub", cx + 9, cy + 15.5, s) + "</g>")
            cx += w + 6
        assert cx <= x1 - 6
        cy += 28
    y1 = cy + 6
    frame = f'<rect class="f-record-ledger" x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" rx="12"/>'
    return frame + "".join(P), "".join(flows), y1


def _defs(pre, x, y, w, h):
    return (f'<defs><linearGradient id="{pre}-pnl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="f-record-g0"/>'
            f'<stop offset="1" class="f-record-g1"/></linearGradient>'
            f'<clipPath id="{pre}-clip"><rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"/></clipPath></defs>')


LEGEND = [("flow", "trace: each step a pulse"), ("amber", "paused for review"), ("dia", "checkpoint saved"),
          ("okc", "a person approves")]
LABEL = ("An oscilloscope trace of one chained run, with a run record beside it; times are illustrative. Harness controls "
         "you set: database writes full, append-only or read-only (here append-only); on a failed step halt, ask or skip "
         "(here ask); partial results kept; post-run output checks on schema, result count, keywords, metric thresholds "
         "and latency (here three of the five on). The run's events scroll past a write head, each step a pulse. The run "
         "starts and its input is stored with secrets redacted. Step 1 runs and a checkpoint is saved. Step 2 fails and a "
         "checkpoint is saved; under ask, the run pauses for human review and the trace flat-lines in amber until a person "
         "approves. Then step 2 re-runs, while step 1 keeps its result and is not re-run, and step 3 runs, each followed by "
         "a checkpoint. The run keeps one checkpoint and each save replaces the last, so once approved the failed result is "
         "dropped from it and remains in the event stream. When the run completes, its outputs, metrics and trace are stored. Every event goes to the "
         "run's stored event stream. A run can be paused, resumed, cancelled and replayed, and a report generated from its "
         "record. Values are illustrative.")


def _controls(v, r, layout):
    """The four harness controls (C26); layout gives each control's anchor and each check's text position."""
    k1, (l1, r1) = _knob(*layout["w"], r, ("full", "append-only", "read-only"), 1, "WRITES", v)
    k2, (l2, r2) = _knob(*layout["f"], r, ("halt", "ask", "skip"), 1, "FAILED STEP", v)
    sw, sw_r = _switch(*layout["p"], "PARTIAL RESULTS", v)
    P = [k1, k2, _ring(*layout["f"], r, "ask", v), sw]
    for (s, on), (x, y) in zip(CHECKS, layout["c"]):
        P.append(_box(x, y, on, s))
    P.append(_txt("hdr f-record-pm", layout["c"][0][0], layout["ct"], "OUTPUT CHECKS"))
    return "".join(P), (l1, r1, l2, r2, sw_r)


def _wide():
    W, v, pre = 1100, "wide", "rc-w"
    PX0, PX1, PT = 30, 790, 46
    SX0, SX1, SY0, SY1 = 50, 770, 88, 345
    GB0, GB1 = 137, 287  # grid band: the trace's only region; labels sit in the strips above and below
    XL, XR = SX0 + 14, SX1 - 14  # u = 0 and the write head (u = 100)
    g = _Geo(v, XL, (XR - XL) / 100, 238, 88)
    assert g.p(0, 1.1)[1] - 3 >= GB0 and g.p(0, -.4)[1] + 8 <= GB1
    LY0, LX0, LX1 = PT, 812, 1070
    P = [_defs(pre, SX0, SY0, XR - SX0, SY1 - SY0), hdr(30, 30, "EVENT TRACE · ONE CHAINED RUN"), hdr(LX0, 30, "RUN RECORD")]
    PB = 470
    P.append(f'<rect class="panel f-record-hous" x="{PX0}" y="{PT}" width="{PX1 - PX0}" height="{PB - PT}" rx="18" '
             f'style="fill:url(#{pre}-pnl)"/>')
    P.append(f'<rect class="f-record-scr" x="{SX0}" y="{SY0}" width="{SX1 - SX0}" height="{SY1 - SY0}" rx="8"/>')
    P.append(_txt("hdr f-record-pm", SX0, 74, "CH1 · RUN EVENTS"))
    P.append(_status(560, 74, v))
    # graticule in the grid band only (the label strips stay clear), ground marker, write head
    for k in range(5):
        y = GB0 + k * (GB1 - GB0) / 4
        P.append(f'<path class="f-record-grid" d="M{SX0},{f(y)} H{SX1}"/>')
    for k in range(10):
        x = XL + k * (XR - XL) / 10
        P.append(f'<path class="f-record-grid" d="M{f(x)},{GB0} V{GB1}"/>')
    P.append(f'<path class="f-record-gnd" d="M{SX0 - 10},{238 - 5} l8,5 l-8,5 z"/>')
    P.append(f'<path class="f-record-head" d="M{XR},{GB0} V{GB1}"/><path class="f-record-gnd" d="M{XR - 5},{SY0 - 9} h10 l-5,7 z"/>')
    # the scrolled layer
    S = _trace(g, v)
    # pause bracket in the top strip, its label above
    xa, xb = g.p(U_PAUSE)[0], g.p(U_RESUME)[0]
    S.append(f'<path class="f-record-bk" d="M{f(xa)},{GB0 - 2} V129 H{f(xb)} V{GB0 - 2}"/>')
    um = (U_PAUSE + U_RESUME) / 2
    w = len(ASK) * LBL[v]
    assert w <= xb - xa - 8
    S.append(_timed("lbl f-record-pi", g.p(um)[0], 120, ASK, U_PAUSE, tau(um + w / 2 / g.k) + REVEAL, "middle"))
    spans = {"top": [], "low": []}
    for s, ue, band, an, ua in LABELS:
        w = len(s) * CW[v]
        x = g.p(ua)[0]
        lo = {"start": x, "middle": x - w / 2, "end": x - w}[an]
        spans[band].append((lo, lo + w))
        y = 120 if band == "top" else 304
        S.append(_timed("sub f-record-pi", x, y, s, ue, tau((lo + w - XL) / g.k) + REVEAL, an))
    spans["top"].append((xa, xb))
    for band in spans.values():
        band.sort()
        assert all(b[0] - a[1] >= 8 for a, b in zip(band, band[1:])), band
        assert band[0][0] >= SX0 + 2 and band[-1][1] <= XR - 3, band
    # time axis with the break, ticks and timestamps
    tg = _Geo(v, XL, g.k, 312, 88)  # the time axis runs under the trace
    S.append(f'<path class="f-record-ax" d="{tg.path([(0, 0), (BREAK[0], 0)])} {tg.path([(BREAK[1], 0), (100, 0)])}"/>')
    S.append(_slashes(tg, 0, "f-record-brk ax"))
    for s, u in TIMES:
        x = g.p(u)[0]
        w = len(s) * CW[v]
        an = "end" if u == 100 else "middle"
        xr = x if an == "end" else x + w / 2
        if u == 100:
            x -= 3
            xr -= 3
        S.append(f'<path class="f-record-tk" d="M{f(g.p(u)[0])},312 v5"/>')
        S.append(_timed("sub f-record-pm", x, 333, s, u, tau((xr - XL) / g.k) + REVEAL, an))
    P.append(f'<g clip-path="url(#{pre}-clip)"><g class="f-record-scroll" data-x0="{f(XR - XL)}" '
             f'data-x1="{f(SX0 - XR)}" data-d="{_tv(D)}">' + "".join(S) + "</g></g>")
    P.append(_pen(XR, 238))
    # harness controls under the screen
    hy = 368
    lab = "HARNESS CONTROL · SET BY YOU"
    P.append(_txt("hdr f-record-pm", SX0, hy, lab))
    P.append(f'<path class="f-record-div" d="M{f(SX0 + len(lab) * HW[v] + 14)},{hy - 4} H{SX1}"/>')
    cy = 414
    # checks read row-wise in two columns: schema, result count / keywords, thresholds / latency
    layout = {"w": (111, cy), "f": (291, cy), "p": (378, cy, cy + 18 + 24),
              "c": [(552 + 92 * (j % 2), cy - 20 + 20 * (j // 2)) for j in range(len(CHECKS))], "ct": cy + 18 + 24}
    ctl, (l1, r1, l2, r2, sw_r) = _controls(v, 18, layout)
    assert SX0 <= l1 and r1 + 16 <= l2 and r2 + 16 <= 378 and sw_r + 16 <= 552, (l1, r1, l2, r2, sw_r)
    assert 552 + 92 + 17 + len("result count") * CW[v] <= SX1 - 8
    P.append(ctl)
    assert cy + 18 + 24 + 12 <= PB
    # ledger and the connector from the write head
    inlet = curve_d(SX1, 238, LX0 - 2, LY0 + 24)  # level with a new slip (top - 10 + 14), clear of the frame's corner
    led, flows, ly1 = _ledger(LX0, LX1, LY0, v, inlet)
    P.append(f'<path class="cv" d="{inlet}" marker-end="url(#arr)"/>')
    P.append(led + flows)
    H = max(ly1, PB) + 44
    P.append(legend(LEGEND, 30, H - 18) + note(W - 30 - 23 * CW[v], H - 18))
    assert 30 + sum(30 + int(len(t) * 8.1) + 22 for _, t in LEGEND) < W - 30 - 23 * CW[v]
    return svg(W, round(H), "".join(P), v, LABEL)


def _narrow():
    W, v, pre = 360, "narrow", "rc-n"
    PX0, PX1, PT = 12, 348, 40
    P = [hdr(12, 24, "EVENT TRACE · ONE CHAINED RUN")]
    # controls first (set before the run), then the screen
    hy = PT + 28
    P.append(_txt("hdr f-record-pm", PX0 + 10, hy, "HARNESS CONTROL · SET BY YOU"))
    cy1 = hy + 66
    cy2 = cy1 + 116
    layout = {"w": (80, cy1), "f": (268, cy1), "p": (24, cy2, cy2 + 58),
              "c": [(190, cy2 - 40 + 20 * j) for j in range(len(CHECKS))], "ct": cy2 + 58}
    ctl, (l1, r1, l2, r2, sw_r) = _controls(v, 16, layout)
    assert PX0 + 8 <= l1 and r1 + 10 <= l2 and r2 <= PX1 - 8 and sw_r + 8 <= 190, (l1, r1, l2, r2, sw_r)
    assert 190 + 17 + len("result count") * CW[v] <= PX1 - 8
    P.append(ctl)
    dv = cy2 + 76
    P.append(f'<path class="f-record-div" d="M{PX0 + 10},{dv} H{PX1 - 10}"/>')
    by = dv + 26
    P.append(_txt("hdr f-record-pm", PX0 + 10, by, "CH1 · EVENTS"))
    P.append(_status(186, by, v))
    assert 197 + len("paused for review") * CW[v] <= PX1 - 6
    SX0, SX1, SY0 = 22, 338, by + 14
    K = 5.6
    TC1, GB0, GB1, LC0 = 72, 78, 196, 206  # time column | grid band | label column
    g = _Geo(v, SY0 + 14, K, GB0 + 4 + .4 * 64, 64)
    assert g.p(0, 1.1)[0] + 3 <= GB1 and g.p(0, -.4)[0] - 7 >= TC1 + 3
    YH = g.p(100)[1]  # the write head
    SY1 = YH + 14
    PB = SY1 + 16
    P.insert(0, _defs(pre, SX0, SY0, SX1 - SX0, YH - SY0))
    P.insert(1, f'<rect class="panel f-record-hous" x="{PX0}" y="{PT}" width="{PX1 - PX0}" height="{PB - PT}" rx="18" '
                f'style="fill:url(#{pre}-pnl)"/>')
    P.append(f'<rect class="f-record-scr" x="{SX0}" y="{SY0}" width="{SX1 - SX0}" height="{SY1 - SY0}" rx="8"/>')
    for k in range(5):
        x = GB0 + k * (GB1 - GB0) / 4
        P.append(f'<path class="f-record-grid" d="M{f(x)},{SY0 + 4} V{f(YH)}"/>')
    for k in range(10):
        y = g.p(k * 10)[1]
        P.append(f'<path class="f-record-grid" d="M{GB0},{f(y)} H{GB1}"/>')
    P.append(f'<path class="f-record-gnd" d="M{f(g.base - 5)},{SY0 - 9} h10 l-5,7 z"/>')
    P.append(f'<path class="f-record-head" d="M{GB0},{f(YH)} H{GB1}"/><path class="f-record-gnd" d="M{PX0 + 1},{f(YH - 5)} l7,5 l-7,5 z"/>')
    S = _trace(g, v)
    ya, yb = g.p(U_PAUSE)[1], g.p(U_RESUME)[1]
    S.append(f'<path class="f-record-bk" d="M{GB1 + 2},{f(ya)} H{LC0 - 2} V{f(yb)} H{GB1 + 2}"/>')
    um = (U_PAUSE + U_RESUME) / 2
    ym = g.p(um)[1]
    rows = []
    for j, s in enumerate(ASK_N):
        assert len(s) * LBL[v] <= SX1 - 6 - (LC0 + 6)
        y = ym - 4 + 18 * j
        rows.append((y - 10, y + 3))
        S.append(_timed("lbl f-record-pi", LC0 + 6, y, s, U_PAUSE, tau(um + (18 * j - 1) / K) + REVEAL))  # its bottom past the head
    for s, ue, band, an, ua in LABELS:
        ur = {"run complete": 98, "run starts": ue}.get(s, ua)  # narrow rows: inside the head, at the event
        y = g.p(ur)[1] + 4.5
        assert LC0 + len(s) * CW[v] <= SX1 - 6, s
        rows.append((y - 10, y + 3))
        S.append(_timed("sub f-record-pi", LC0, y, s, ue, tau(ur + 7.5 / K) + REVEAL))
    rows.sort()
    assert all(b[0] - a[1] >= 4 for a, b in zip(rows, rows[1:])), rows
    ax = " ".join(f"M{TC1},{f(g.p(a)[1])} V{f(g.p(b)[1])}" for a, b in ((0, BREAK[0]), (BREAK[1], 100)))
    S.append(f'<path class="f-record-ax" d="{ax}"/>')
    S.append(_slashes(_Geo(v, SY0 + 14, K, TC1, 64), 0, "f-record-brk ax"))
    for s, u in TIMES:
        ur = 98 if u == 100 else u
        y = g.p(ur)[1]
        S.append(f'<path class="f-record-tk" d="M{TC1},{f(g.p(u)[1])} h-4"/>')
        assert TC1 - 6 - len(s) * CW[v] >= SX0 + 3
        S.append(_timed("sub f-record-pm", TC1 - 6, y + 4.5, s, u, tau(ur + 7.5 / K) + REVEAL, "end"))
    P.append(f'<g clip-path="url(#{pre}-clip)"><g class="f-record-scroll" data-x0="{f(YH - g.t0)}" '
             f'data-x1="{f(SY0 - YH)}" data-d="{_tv(D)}">' + "".join(S) + "</g></g>")
    P.append(_pen(g.base, YH))
    LY0 = PB + 44
    inlet = vcurve_d(g.base, SY1 + 2, 180, LY0 - 2)
    led, flows, ly1 = _ledger(12, 348, LY0, v, inlet)
    P.append(f'<path class="cv" d="{inlet}" marker-end="url(#arr)"/>')
    P.append(hdr(196, PB + 30, "RUN RECORD"))
    P.append(led + flows)
    ly = ly1 + 34
    P.append("".join(legend([it], 12, ly + 26 * k) for k, it in enumerate(LEGEND)) + note(12, ly + 26 * len(LEGEND)))
    return svg(W, round(ly + 26 * len(LEGEND) + 14), "".join(P), v, LABEL)


JS = """MAFig.register("record", function (root, variant) {
  var q = function (s) { return gsap.utils.toArray(root.querySelectorAll(s)); };
  var wide = variant === "wide", scr = root.querySelector(".f-record-scroll"), pen = root.querySelector(".f-record-pen");
  var X0 = +scr.getAttribute("data-x0"), X1 = +scr.getAttribute("data-x1");
  var SX = wide ? X0 : 0, SY = wide ? 0 : X0;  // the run's start sits at the write head
  var ping = pen.querySelector(".f-record-ping"), amp = wide ? 88 : 64;
  var WAVE = __WAVE__, EV = __EV__, D = __D__;
  var tau = function (u) { return u / 100 * D; };
  q(".f-record-kp").forEach(function (p) { gsap.set(p, {svgOrigin: p.getAttribute("data-o")}); });
  // everything a pass reveals is registered here, and the loop clears exactly this list
  var timed = q("[data-t]"), windows = q("[data-w]"), shown = timed.concat(windows);
  // one pass from t0: the trace scrolls u = 0..100 past the write head at a constant rate while the pen follows the
  // waveform; a label, tick or record shows only after its event has passed the head, and records drop onto the
  // ledger after flowing along the connector. Every key in a fromTo start object is repeated in its end object.
  function pass(tl, t0) {
    tl.fromTo(scr, {x: SX, y: SY}, {x: 0, y: 0, duration: D, ease: "none"}, t0);
    for (var i = 1; i < WAVE.length; i++) {
      var a = WAVE[i][1];
      tl.to(pen, {x: wide ? 0 : a * amp, y: wide ? -a * amp : 0, duration: tau(WAVE[i][0] - WAVE[i - 1][0]), ease: "none"}, t0 + tau(WAVE[i - 1][0]));
    }
    EV.forEach(function (u) {
      tl.fromTo(ping, {opacity: .9, attr: {r: 5}}, {opacity: 0, attr: {r: 16}, duration: .5, ease: "power1.out", immediateRender: false}, t0 + tau(u));
    });
    windows.forEach(function (el) {
      el.getAttribute("data-w").split(" ").forEach(function (s, k) {
        if (k === 0) tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: .2}, t0 + +s);
        else tl.to(el, {opacity: k % 2 ? 0 : 1, duration: .2}, t0 + +s);
      });
    });
    timed.forEach(function (el) {
      var t = t0 + +el.getAttribute("data-t");
      if (el.classList.contains("f-record-slip")) {
        tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: .12, ease: "none"}, t)
          .fromTo(el, {y: -el.getAttribute("data-dy")}, {y: 0, duration: __DROP__, ease: "bounce.out"}, t);
      } else tl.fromTo(el, {opacity: 0}, {opacity: 1, duration: .25}, t);
    });
    q(".f-record-flow").forEach(function (fl) {
      var t = t0 + +fl.getAttribute("data-f");
      tl.set(fl, {opacity: 1}, t)
        .fromTo(fl, {drawSVG: "0% 0%"}, {drawSVG: "70% 100%", duration: __FLOWD__, ease: "power1.in"}, t)
        .to(fl, {opacity: 0, duration: .12}, t + __FLOWD__);
    });
  }
  var intro = gsap.timeline({defaults: {ease: "power3.out"}});
  intro.from(q(".hdr:not(.f-record-pm), .legend, .f-record-ledger, .f-record-rule, .f-record-tick:not(.on), .f-record-chip, .f-record-lt, .cv"), {opacity: 0, duration: .5}, 0)
    .from(q(".f-record-hous"), {opacity: 0, duration: .5}, .05)
    .from(q(".f-record-scr"), {opacity: 0, duration: .4}, .15)
    .from(q(".f-record-grid"), {drawSVG: "0%", duration: .5, stagger: .015}, .25)
    .from(q(".hdr.f-record-pm, .f-record-div, .f-record-head, .f-record-knob, .f-record-gnd, .f-record-sw, .f-record-cb, .f-record-cbt, .f-record-kd, " +
            ".sub.f-record-pm:not([data-t]), .sub.f-record-pi:not([data-t]):not([data-w])"), {opacity: 0, duration: .4, stagger: .008}, .35)
    .from(q(".f-record-kp"), {rotation: function (i, p) { return -p.getAttribute("data-a"); }, duration: .6, ease: "back.out(1.6)"}, .7)
    .from(q(".f-record-swk"), {x: -20, duration: .5}, .7)
    .set(shown, {opacity: 0}, 0)
    .set(q(".f-record-flow"), {opacity: 0}, 0)
    .set(scr, {x: SX, y: SY}, 0);
  pass(intro, __T0I__);
  // loop: hold the finished run, clear what the pass reveals, sweep the old trace off the screen, run again.
  // immediateRender off: the frame stays until then.
  var loop = gsap.timeline({repeat: -1, defaults: {immediateRender: false}});
  loop.to(shown, {opacity: 0, duration: .4}, __HOLD__)
    .to(scr, {x: wide ? X1 : 0, y: wide ? 0 : X1, duration: .8, ease: "power2.in"}, __HOLD__ + .2);
  pass(loop, __T0L__);
  loop.set({}, {}, __TL__);
  return {intro: intro, loop: loop};
});"""
for _k, _v in {"__WAVE__": json.dumps([[u, a] for u, a in WAVE], separators=(",", ":")),
               "__EV__": json.dumps([u for u, _a in EVENTS]), "__D__": _tv(D), "__DROP__": _tv(DROP_D),
               "__FLOWD__": _tv(FLOW_D), "__T0I__": _tv(T0_INTRO), "__HOLD__": _tv(HOLD), "__T0L__": _tv(T0_LOOP),
               "__TL__": _tv(T_LOOP)}.items():
    JS = JS.replace(_k, _v)
assert "__" not in JS


def build():
    return Figure(wide=_wide(), narrow=_narrow(), js=JS)
