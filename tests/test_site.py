import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "index.html").read_text(encoding="utf-8") if (ROOT / "index.html").exists() else ""

EXPECTED_SECTIONS = ["opening", "modules", "literature", "gaps", "hypotheses", "planning", "vasp", "domains", "scores", "record", "improvement", "interfaces", "contact"]
FORBIDDEN = [r"\bautonomous", r"self-driving", r"closed[- ]loop", r"discover(s|ed|ing)? new materials",
  r"\bvalidated\b", r"33 sub-modes",
  r"recall@\d\s*(=|:|of)", r"win rate", r"hits@", r"\bMRR\b", r"bayesian optimi[sz]", r"active learning",
  r"surrogate", r"uncertainty quantification", r"reflexion", r"local (llm|model)s?",
  r"structure generation", r"send to maestro", 
  r"slab generation", r"air-gapped"]

TOKENS = {
    "light": {"bg": "#F6F8FB", "dot": "#D5DDE8", "ink": "#0B1220", "muted": "#4B5970",
              "line": "#C3CEDC", "line-strong": "#8C9AB0", "panel": "#0f1622", "panel-ink": "#EAF2F8", "panel-muted": "#8FA3BC", "node": "#FFFFFF", "accent": "#0E7F78", "accent-2": "#9A600E"},
    "dark": {"bg": "#0A0F1A", "dot": "#1A2538", "ink": "#E6EDF5", "muted": "#8A97AB",
             "line": "#24324A", "line-strong": "#4A5B78", "node": "#101A2B", "accent": "#4FD1C5", "accent-2": "#F5B544"},
}


def visible_text(html):
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    labels = " ".join(re.findall(r'aria-label="([^"]*)"', html))
    return re.sub(r"<[^>]+>", " ", html) + " " + labels


def css():
    return "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", PAGE, flags=re.S))


def _decls(block):
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})", block))


def _block(selector_re):
    m = re.search(selector_re + r"\s*\{([^}]*)\}", css())
    return m.group(1) if m else ""


def tokens(theme):
    if theme == "light":
        return _decls(_block(r":root(?!\[|:)"))
    return _decls(_block(r':root\[data-theme="dark"\]'))


def _media_dark_tokens():
    return _decls(_block(r':root:not\(\[data-theme="light"\]\)'))


def _lum(hex_):
    def ch(i):
        c = int(hex_[1 + 2 * i:3 + 2 * i], 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(0) + 0.7152 * ch(1) + 0.0722 * ch(2)


def contrast(fg, bg):
    a, b = sorted((_lum(fg), _lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def parse_claims(text):
    out = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and re.fullmatch(r"C\d{2}", cells[0]):
            out[cells[0]] = cells[-1].lower()
    return out


def claims():
    """The claims register lives in the private CATAGENT repo (docs/site/claims.md); None when absent."""
    p = Path(os.environ.get("CATAGENT_REPO", str(ROOT.parent / "CATAGENT"))) / "docs" / "site" / "claims.md"
    return parse_claims(p.read_text(encoding="utf-8")) if p.exists() else None


class SiteTests(unittest.TestCase):
    def test_title_and_meta(self):
        self.assertIn("<title>MatAgent · Research agent for materials science</title>", PAGE)
        m = re.search(r'<meta name="description" content="([^"]+)"', PAGE)
        self.assertTrue(m and m.group(1).strip())
        self.assertIn('<html lang="en-GB"', PAGE)

    def test_tokens_exact(self):
        for theme in ("light", "dark"):
            self.assertEqual(tokens(theme), TOKENS[theme], theme)

    def test_contrast(self):
        for theme, t in ((k, tokens(k)) for k in ("light", "dark")):
            for fg in ("ink", "muted", "accent", "accent-2"):
                for bg in ("bg", "node"):
                    self.assertGreaterEqual(contrast(t[fg], t[bg]), 4.5, f"{theme} {fg} on {bg}")
            self.assertGreaterEqual(contrast(t["bg"], t["accent"]), 4.5, f"{theme} bg on accent")
        # the dark focal panel keeps its own ink in both themes (defined once on :root)
        light = tokens("light")
        for fg in ("panel-ink", "panel-muted"):
            self.assertGreaterEqual(contrast(light[fg], light["panel"]), 4.5, fg)

    def test_theme_selectors(self):
        self.assertTrue(tokens("dark"))
        self.assertEqual(_media_dark_tokens(), tokens("dark"))
        self.assertIn("@media (prefers-color-scheme: dark)", css())
        script = re.search(r"<script>(.*?)</script>", PAGE, flags=re.S).group(1)
        self.assertIn('localStorage.getItem("matagent-theme")', script)
        self.assertIn("dataset.theme", script)
        self.assertLess(PAGE.index('"matagent-theme"'), PAGE.index("<style"))

    def test_theme_toggle(self):
        self.assertRegex(PAGE, r'<button[^>]*id="theme-toggle"[^>]*aria-pressed=')

    def test_external_hosts(self):
        scripts = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", PAGE, flags=re.S))
        urls = re.findall(r'(?:src|href)="(https?://[^"]+)"', PAGE)
        urls += re.findall(r"""url\(\s*['"]?(https?://[^'")\s]+)""", css())
        urls += re.findall(r"""@import\s+(?:url\(\s*)?['"]?(https?://[^'")\s;]+)""", css())
        urls += re.findall(r"""fetch\(\s*['"`]?(https?://[^'"`)\s]+)""", scripts)
        for url in urls:
            self.assertIn(re.match(r"https?://([^/]+)", url).group(1),
                          {"fonts.googleapis.com", "fonts.gstatic.com"}, url)
        for src in re.findall(r'<script[^>]*\bsrc="([^"]+)"', PAGE):
            self.assertRegex(src, r"^assets/vendor/gsap/(gsap|ScrollTrigger|DrawSVGPlugin|MorphSVGPlugin)\.min\.js$")
        # any fetch() at all must target a literal allowed URL, never a computed one
        self.assertEqual(len(re.findall(r"\bfetch\(", scripts)),
                         len(re.findall(r"""fetch\(\s*['"`]https?://""", scripts)))

    def test_font_fallbacks(self):
        fams = re.findall(r"font-family:\s*([^;}]+)", css())
        self.assertTrue(fams)
        for f in fams:
            self.assertRegex(f.strip(), r"(serif|sans-serif|monospace|system-ui)$", f)

    def test_localstorage_guarded(self):
        self.assertEqual(PAGE.count("localStorage"),
                         len(re.findall(r"try\s*\{[^}]*localStorage", PAGE)))

    def test_reduced_motion(self):
        m = re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?\})\s*\}", css(), flags=re.S)
        self.assertTrue(m)
        self.assertIn(".particle", m.group(1))
        self.assertIn("display: none", m.group(1))

    def test_svgs_accessible(self):
        for tag in re.findall(r"<svg\b[^>]*>", PAGE):
            if 'aria-hidden="true"' in tag and 'width="0"' in tag:  # the hidden shared-symbols sprite only
                continue
            # a figure with keyboard-focusable tiles is a group, so its tiles stay in the accessibility tree
            self.assertIn('role="group"' if 'data-fig-tiles="1"' in tag else 'role="img"', tag)
            m = re.search(r'aria-label="([^"]*)"', tag)
            self.assertTrue(m and len(m.group(1)) >= 20, tag)
        # the group exemption: only tabindex="0" tiles are exposed; all other content sits in one aria-hidden group
        groups = re.findall(r'<svg\b[^>]*role="group"[^>]*>(.*?)</svg>', PAGE, flags=re.S)
        for body in groups:
            m = re.fullmatch(r'<g aria-hidden="true">.*?</g>((?:<g [^>]*tabindex="0"[^>]*>.*?<!--/tile-->)+)', body, flags=re.S)
            self.assertTrue(m, body[:120])
            self.assertNotIn('aria-hidden', m.group(1))

    def test_figs_have_narrow(self):
        for fig in re.findall(r'<figure class="fig".*?</figure>', PAGE, flags=re.S):
            self.assertEqual(len(re.findall(r'<svg[^>]*class="sch wide"', fig)), 1)
            self.assertEqual(len(re.findall(r'<svg[^>]*class="sch narrow"', fig)), 1)

    def test_font_families_geist_only(self):
        for f in re.findall(r"font-family:\s*([^;}]+)", css()):
            first = f.split(",")[0].strip().strip("\"'")
            self.assertIn(first, ("Geist", "Geist Mono", "inherit"), f)
        self.assertIsNone(re.search(r"Newsreader|\bInter\b|JetBrains", PAGE))

    def test_brand_assets_verbatim(self):
        repo = os.environ.get("CATAGENT_REPO", str(ROOT.parent / "CATAGENT"))
        if not Path(repo).exists():
            self.skipTest("CATAGENT repo not present")
        for dst, src in (("assets/matagent-mark.svg", "frontend/src/assets/catagent-mark.svg"),
                         ("assets/favicon.svg", "frontend/public/matagent-favicon.svg")):
            want = subprocess.run(["git", "-C", repo, "show", "bc983737:" + src],
                                  capture_output=True, check=True).stdout
            self.assertEqual((ROOT / dst).read_bytes(), want, dst)

    def test_no_bare_svg_selector(self):
        for sel in re.findall(r"([^{}]+)\{", re.sub(r"/\*.*?\*/", "", css(), flags=re.S)):
            self.assertNotEqual(sel.strip(), "svg")
            self.assertNotIn("svg", [x.strip() for x in sel.split(",")])

    def test_header_lockup(self):
        h = re.search(r"<header.*?</header>", PAGE, flags=re.S).group(0)
        self.assertIn('<img src="assets/matagent-mark.svg" alt="" width="38" height="38">', h)
        self.assertIn("Materials Research Agent", h)
        self.assertIn("MatAgent", re.sub(r"Materials Research Agent", "", h))

    def test_edges_have_pathlength(self):
        for svg in re.findall(r"<svg\b[^>]*class=\"[^\"]*\bsch\b.*?</svg>", PAGE, flags=re.S):
            for tag in re.findall(r"<[a-z]+\b[^>]*class=\"[^\"]*\bedge\b[^>]*>", svg):
                self.assertIn('pathLength="1"', tag)

    def test_hidden_state_gated_by_js(self):
        self.assertIn('classList.add("js")', PAGE)
        for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", re.sub(r"/\*.*?\*/", "", css(), flags=re.S)):
            if re.search(r"opacity:\s*0\b|stroke-dashoffset:\s*1\b", body):
                self.assertTrue(all(x.strip().startswith(".js ") for x in sel.split(",")), sel)

    def test_reduced_motion_covers_dashed_connectors(self):
        m = re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?\})\s*\}", css(), flags=re.S)
        self.assertIn(".sch .dash", m.group(1))

    def test_reduced_motion_hides_highlights(self):
        # glow windows that start at t = 0 would leave a node lit in the static frame
        m = re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?\})\s*\}", css(), flags=re.S)
        self.assertRegex(m.group(1), r"\.sch \.hl\s*\{[^}]*visibility:\s*hidden")

    def test_dash_not_edge(self):
        # dashed connectors never take pathLength (it rescales the dash) and never share the edge draw-in
        tags = re.findall(r"<[a-z]+\b[^>]*class=\"[^\"]*\bdash\b[^>]*>", PAGE)
        self.assertTrue(tags)  # the remaining SMIL figures still use dashed connectors
        self.assertNotRegex(PAGE, r'class="[^"]*\bedge (opt|rej)\b')
        for tag in tags:
            self.assertNotRegex(tag, r'class="[^"]*\bedge\b')
            self.assertNotIn("pathLength", tag)

    def test_fig_breakpoint(self):
        m = re.search(r"@media \(max-width: ([\d.]+px)\) \{[^{}]*\.fig \.wide \{ display: none; \}", css())
        self.assertTrue(m)
        self.assertIn(m.group(1), ("1000px", "999.98px"))

    def test_sections_in_order(self):
        ids = re.findall(r'<section[^>]*\bid="([^"]+)"', PAGE)
        self.assertEqual(ids, EXPECTED_SECTIONS)

    def test_mail_links(self):
        want = {"mailto:lohgc@a-star.edu.sg?subject=MatAgent%20early%20access",
                "mailto:lohgc@a-star.edu.sg?subject=MatAgent%20collaboration"}
        self.assertEqual(set(re.findall(r'href="(mailto:[^"]+)"', PAGE)), want)

    def test_affiliation(self):
        aff = "A*STAR IAIC Sustainability Directorate"
        card = re.search(r'<section[^>]*id="contact".*?<address class="ccard">(.*?)</address>', PAGE, flags=re.S)
        self.assertTrue(card)
        self.assertIn(aff, card.group(1))
        self.assertIn(aff, re.search(r"<footer.*?</footer>", PAGE, flags=re.S).group(0))

    def test_scroll_margin_clears_header(self):
        # nav anchors must not land under the sticky header (min-height + 1 px border)
        h = int(re.search(r"\.site-header \.wrap \{[^}]*min-height:\s*(\d+)px", css()).group(1)) + 1
        m = re.search(r"section\[id\]\s*\{[^}]*scroll-margin-top:\s*(\d+)px", css())
        self.assertTrue(m)
        self.assertEqual(int(m.group(1)), h)

    def test_color_scheme_per_theme(self):
        self.assertNotIn("color-scheme: light dark", css())
        self.assertIn("color-scheme: light;", _block(r":root(?!\[|:)"))
        self.assertIn("color-scheme: dark;", _block(r':root\[data-theme="dark"\]'))
        self.assertIn("color-scheme: dark;", _block(r':root:not\(\[data-theme="light"\]\)'))

    def test_toggle_hit_area(self):
        m = re.search(r"#theme-toggle\s*\{([^}]*)\}", css())
        self.assertTrue(m)
        for prop in ("min-width", "min-height"):
            self.assertGreaterEqual(int(re.search(prop + r":\s*(\d+)px", m.group(1)).group(1)), 44, prop)
        hdr = int(re.search(r"\.site-header \.wrap \{[^}]*min-height:\s*(\d+)px", css()).group(1))
        self.assertGreaterEqual(hdr, 44)

    def test_forbidden_terms(self):
        text = visible_text(PAGE)
        for pat in FORBIDDEN:
            self.assertIsNone(re.search(pat, text, re.I), pat)

    def test_nav_targets(self):
        nav = re.search(r'<nav.*?</nav>', PAGE, flags=re.S).group(0)
        hrefs = re.findall(r'href="#([^"]+)"', nav)
        self.assertEqual(hrefs, ["literature", "gaps", "hypotheses", "planning", "vasp", "domains",
                                 "scores", "record", "improvement", "interfaces"])

    @staticmethod
    def _script(sid):
        m = re.search(r'<script id="%s">(.*?)</script>' % sid, PAGE, flags=re.S)
        return m.group(1) if m else ""

    def test_gsap_vendored(self):
        d = ROOT / "assets" / "vendor" / "gsap"
        names = ("gsap", "ScrollTrigger", "DrawSVGPlugin", "MorphSVGPlugin")
        files = [d / f"{n}.min.js" for n in names]
        for f in files:
            self.assertTrue(f.exists(), f)
        self.assertLessEqual(sum(f.stat().st_size for f in files), 200_000)
        self.assertIn("gsap.com/standard-license", (d / "LICENSE.txt").read_text(encoding="utf-8"))
        order = [PAGE.index(f'src="assets/vendor/gsap/{f.name}"') for f in files]
        self.assertEqual(order, sorted(order))
        self.assertLess(order[-1], PAGE.index('<script id="figrt">'))
        self.assertLess(PAGE.index('<script id="figrt">'), PAGE.index('<script id="figjs">'))
        self.assertNotRegex(PAGE, r'<script[^>]*src="assets/vendor[^>]*\b(defer|async)\b')

    def test_generator_check_clean(self):
        r = subprocess.run([sys.executable, "tools/figures.py", "--check"], cwd=ROOT)
        self.assertEqual(r.returncode, 0)

    def test_generator_check_detects_stale(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "index.html"
            tmp.write_text(PAGE.replace("<!-- symbols:start -->", "<!-- symbols:start --><symbol id=\"stale\"/>", 1), encoding="utf-8")
            env = dict(os.environ, FIGURES_INDEX=str(tmp))
            self.assertEqual(subprocess.run([sys.executable, "tools/figures.py", "--check"], cwd=ROOT, env=env).returncode, 1)
            subprocess.run([sys.executable, "tools/figures.py"], cwd=ROOT, env=env, check=True)
            self.assertEqual(tmp.read_text(encoding="utf-8"), PAGE)

    def test_generator_idempotent(self):
        before = (ROOT / "index.html").read_bytes()
        for _ in range(2):
            subprocess.run([sys.executable, "tools/figures.py"], cwd=ROOT, check=True)
            self.assertEqual((ROOT / "index.html").read_bytes(), before)

    def test_runtime_guards_gsap(self):
        rt = self._script("figrt")
        self.assertTrue(rt)
        self.assertRegex(rt, r"typeof gsap|window\.gsap")

    MQ_WIDE = "(min-width: 1000px) and (prefers-reduced-motion: no-preference)"
    MQ_NARROW = "(max-width: 999.98px) and (prefers-reduced-motion: no-preference)"

    def test_runtime_uses_matchmedia(self):
        rt = self._script("figrt")
        self.assertIn("gsap.matchMedia", rt)
        self.assertIn(self.MQ_WIDE, rt)
        self.assertIn(self.MQ_NARROW, rt)

    def test_runtime_guards_reduced_motion(self):
        rt = self._script("figrt")
        for q in (self.MQ_WIDE, self.MQ_NARROW):
            self.assertIn("(prefers-reduced-motion: no-preference)", q)
            self.assertIn(q, rt)

    def test_runtime_scrub_range(self):
        # the whole scrub range plays while the figure is on screen; never pinned
        rt = self._script("figrt")
        self.assertRegex(rt, r'start: "top 80%", end: "center 45%", scrub: 0\.6')
        self.assertNotIn("pin:", rt)

    def test_no_color_tweens(self):
        for sid in ("figjs", "figrt"):
            self.assertIsNone(re.search(r"[{,]\s*[\"']?(fill|stroke|color|backgroundColor)[\"']?\s*:", self._script(sid)), sid)

    def test_fromto_keys_in_to_vars(self):
        # a key only in fromTo's from-vars is applied through startAt, which a rewind (every loop wrap) reverts and
        # the next pass does not re-apply; so every from-key must also be in the to-vars
        obj = r"\{((?:[^{}]|\{[^{}]*\})*)\}"
        found = 0
        for frm, to in re.findall(r"\.fromTo\([^,]+,\s*" + obj + r",\s*" + obj, self._script("figjs")):
            keys = lambda body: set(re.findall(r"(\w+)\s*:", re.sub(r"\{[^{}]*\}", "", body)))
            self.assertLessEqual(keys(frm), keys(to), (frm, to))
            found += 1
        self.assertTrue(found)

    def test_gsap_figs_registered(self):
        figs = set(re.findall(r'<figure class="fig" data-fig="([^"]+)" data-engine="gsap"', PAGE))
        regs = set(re.findall(r'MAFig\.register\("([^"]+)"', self._script("figjs")))
        self.assertEqual(figs, regs)

    def test_parse_claims(self):
        sample = ("| ID | Claim (site wording basis) | Source @bc983737 (path:lines) | Status |\n"
                  "|---|---|---|---|\n| C01 | a | x.py:1-2 | Confirmed |\n"
                  "| C02 | b | y.py:3 | CHANGED |\n| note | c | d | confirmed |\n")
        self.assertEqual(parse_claims(sample), {"C01": "confirmed", "C02": "changed"})

    def test_claims_statuses(self):
        c = claims()
        if c is None:
            self.skipTest("claims register (CATAGENT docs/site/claims.md) not present")
        self.assertEqual(sorted(c), [f"C{i:02d}" for i in range(1, len(c) + 1)])
        for cid, status in c.items():
            self.assertIn(status, {"confirmed", "changed", "dropped", "assumed"}, cid)

    @staticmethod
    def _visible(fragment):
        import html
        text = html.unescape(re.sub(r"<[^>]+>", "", fragment)).replace("\u2060", "")
        return re.sub(r"\s+", " ", text).strip()

    def test_method_length(self):
        blocks = re.findall(r'<p class="method">(.*?)</p>', PAGE, flags=re.S)
        for b in blocks:
            body = self._visible(re.sub(r"^\s*<b>Method</b>", "", b))
            self.assertLessEqual(len(body), 140, body)

    def test_plain_length(self):
        for b in re.findall(r'<p class="(?:plain|lede)">(.*?)</p>', PAGE, flags=re.S):
            self.assertLessEqual(len(self._visible(b).split()), 30, b)

    def test_caption_length(self):
        for b in re.findall(r"<figcaption>(.*?)</figcaption>", PAGE, flags=re.S):
            self.assertLessEqual(len(self._visible(b)), 120, b)

    def test_no_sep_after_method_label(self):
        for b in re.findall(r'<p class="method">(.*?)</p>', PAGE, flags=re.S):
            self.assertTrue(b.startswith("<b>Method</b>"), b[:40])
            self.assertFalse(self._visible(b)[len("Method"):].lstrip().startswith("·"), b[:40])

    def test_cards_have_claims(self):
        known = claims()
        for tag in re.findall(r'<article class="card"[^>]*>', PAGE):
            m = re.search(r'data-claims="([^"]+)"', tag)
            self.assertTrue(m, tag)
            for cid in m.group(1).split():
                if known is not None:
                    self.assertIn(known.get(cid), ("confirmed", "changed", "assumed"), cid)

    def test_idx_full_opacity(self):
        # .idx is muted text; any opacity below 1 drops it under 4.5:1
        m = re.search(r"\.sch \.idx\s*\{([^}]*)\}", css())
        self.assertTrue(m)
        op = re.search(r"opacity:\s*([\d.]+)", m.group(1))
        self.assertTrue(op is None or float(op.group(1)) >= 1, m.group(1))

    def test_sublabel_length(self):
        import html
        for svg in re.findall(r"<svg\b[^>]*class=\"sch [^\"]*\".*?</svg>", PAGE, flags=re.S):
            for t in re.findall(r'<text class="sub[ "][^>]*>(.*?)</text>', svg, flags=re.S):  # multi-class subs too
                self.assertLessEqual(len(html.unescape(re.sub(r"<[^>]+>", "", t))), 22, t)

    def test_reveal_viewport_based(self):
        # a figure taller than the viewport can never reach a figure-fraction threshold
        script = re.findall(r"<script>(.*?)</script>", PAGE, flags=re.S)[-1]
        opts = re.search(r"new IntersectionObserver\(.*\},\s*(\{[^}]*\})\s*\)", script, flags=re.S)
        self.assertTrue(opts)
        th = re.search(r"threshold:\s*([\d.]+)", opts.group(1))
        self.assertTrue(th is None or float(th.group(1)) == 0, opts.group(1))
        self.assertRegex(opts.group(1), r'rootMargin:\s*"0px 0px -\d+% 0px"')
        self.assertEqual(script.count("new IntersectionObserver"), 1)

    def test_narrow_fig_cap(self):
        m = re.search(r"\.fig \.narrow \{ display: block; max-width: (\d+)px", css())
        self.assertTrue(m)
        self.assertLessEqual(int(m.group(1)), 420)

    def test_opening_plain_language(self):
        import html
        fig = re.search(r'<figure class="fig" data-fig="opening"[^>]*>.*?</figure>', PAGE, flags=re.S).group(0)
        shown = html.unescape(" ".join(re.findall(r'<text class="(?:sub|ttl)"[^>]*>(.*?)</text>', fig)))
        shown += " " + re.search(r"<figcaption>(.*?)</figcaption>", fig, flags=re.S).group(1)
        # plain words, no mode codes or version-like numbers; MatOS routing is not claimed (C42)
        self.assertNotRegex(shown, r"\b(LCA|HF|CDTP|GAR|MMR)\b|\d\.\d|[Vv]alidat")
        self.assertNotIn("MatOS", fig)
        for want in ("Ranked papers", "Cited answers", "Study plan", "New modules", "Run scores", "Run record"):
            self.assertIn(want, shown)
        for label in re.findall(r'aria-label="([^"]*)"', fig):
            for mod in ("SEARCH", "AUGMENT", "PLAN", "DISCOVER", "EVALUATE"):
                self.assertIn(mod, label)

    GSAP_TEXT_MIN = {"wide": 12.8, "narrow": 13.4}  # viewBox units: >= 10.5 px rendered at 1000 px / 360 px

    @staticmethod
    def _css_rules():
        for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", re.sub(r"/\*.*?\*/", "", css(), flags=re.S)):
            m = re.search(r"font-size:\s*([\d.]+)px", body) or re.search(r"font:[^;]*?([\d.]+)px", body)
            if m:
                for piece in sel.split(","):
                    yield piece.strip(), float(m.group(1))

    def test_gsap_text_sizes(self):
        rules = list(self._css_rules())
        for v, low in self.GSAP_TEXT_MIN.items():
            for cls in (".sub", ".hdr", ".tag", ".lbl", ".ttl", ".ttl.sm", ".legend text"):
                scoped = [px for sel, px in rules if '[data-engine="gsap"]' in sel and sel.endswith(" " + cls) and f".sch.{v} " in sel]
                shared = [px for sel, px in rules if '[data-engine="gsap"]' in sel and sel.endswith(" " + cls) and ".sch " in sel]
                got = scoped or shared
                self.assertTrue(got, (v, cls))
                self.assertGreaterEqual(min(got), low, (v, cls))
            for sel, px in rules:
                if f".sch.{v} " in sel:
                    self.assertGreaterEqual(px, low, sel)
        # figure-specific text applies to both variants unless scoped to the wide one
        for sel, px in rules:
            if re.search(r"\.f-[a-z]+-", sel):
                self.assertGreaterEqual(px, self.GSAP_TEXT_MIN["wide" if ".sch.wide " in sel else "narrow"], sel)

    def test_figkit_legend_dash_class(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import figkit
        out = figkit.legend([("dash", "optional")], 0, 0)
        self.assertIn('class="lg-dash"', out)
        for cls in re.findall(r'class="([^"]*)"', out):
            self.assertNotIn("dash", cls.split())  # SMIL-era class
        self.assertRegex(css(), r"\.sch \.lg-dash\s*\{[^}]*stroke-dasharray")

    def test_figkit_hex_constant_stroke(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import figkit
        sym = re.search(r'<symbol id="hex".*?</symbol>', figkit.SYMBOLS).group(0)
        self.assertIn('vector-effect="non-scaling-stroke"', sym)
        self.assertIn('<symbol id="hex"', PAGE)
        self.assertIn('vector-effect="non-scaling-stroke"', re.search(r'<symbol id="hex".*?</symbol>', PAGE).group(0))

    def test_fig_opening(self):
        sec = re.search(r'<section id="opening".*?</section>', PAGE, flags=re.S).group(0)
        fig = re.search(r'<figure class="fig" data-fig="opening" data-engine="gsap">.*?</figure>', sec, flags=re.S)
        self.assertTrue(fig)
        fig = fig.group(0)
        for v in ("wide", "narrow"):
            m = re.search(r'<svg class="sch %s"[^>]*>(.*?)</svg>' % v, fig, flags=re.S)
            self.assertTrue(m, v)
            label = re.search(r'aria-label="([^"]*)"', re.search(r'<svg class="sch %s"[^>]*>' % v, fig).group(0))
            self.assertTrue(label and len(label.group(1)) >= 20, v)
            body = m.group(1)
            self.assertIn('class="legend"', body, v)
            self.assertIn(">MatAgent<", body, v)
            for mod in ("EARCH", "UGMENT", "LAN", "ISCOVER", "VALUATE", "MEMORY"):
                self.assertIn(mod, body, (v, mod))
            # SMIL-era classes stay out of GSAP figures until Task 14 removes the old CSS
            for cls in re.findall(r'class="([^"]*)"', body):
                self.assertFalse({"node", "edge", "dash", "particle", "hl"} & set(cls.split()), (v, cls))
            self.assertNotRegex(body, r"<animate")
        self.assertIn(">chat agent<", fig)  # core sub-label "chat agent · modes", stacked on two lines
        self.assertIn(">modes<", fig)
        for card in re.findall(r'<article class="card"[^>]*>', sec):
            self.assertIn("data-claims=", card)
        self.assertIn('MAFig.register("opening"', self._script("figjs"))
        js = re.search(r'MAFig\.register\("opening".*?<!-- figjs:opening:end -->', self._script("figjs"), flags=re.S)
        self.assertTrue(js)
        self.assertNotIn("scrub", js.group(0))

    def test_fig_modules(self):
        self.assertEqual(EXPECTED_SECTIONS.index("modules"), EXPECTED_SECTIONS.index("opening") + 1)
        sec = re.search(r'<section id="modules".*?</section>', PAGE, flags=re.S)
        self.assertTrue(sec)
        sec = sec.group(0)
        self.assertIn("<h2>Five modules, four capability groups</h2>", sec)
        fig = re.search(r'<figure class="fig" data-fig="modules" data-engine="gsap">.*?</figure>', sec, flags=re.S)
        self.assertTrue(fig)
        fig = fig.group(0)
        for v in ("wide", "narrow"):
            m = re.search(r'<svg class="sch %s"[^>]*>(.*?)</svg>' % v, fig, flags=re.S)
            self.assertTrue(m, v)
            label = re.search(r'aria-label="([^"]*)"', re.search(r'<svg class="sch %s"[^>]*>' % v, fig).group(0))
            self.assertTrue(label and len(label.group(1)) >= 20, v)
            for mod in ("SEARCH", "PLAN", "AUGMENT", "DISCOVER", "EVALUATE"):
                self.assertIn(mod, label.group(1), (v, mod))
            body = m.group(1)
            self.assertIn('class="legend"', body, v)
            self.assertEqual(body.count('class="f-modules-cell"'), 5, v)
            for mod in ("EARCH", "LAN", "UGMENT", "ISCOVER", "VALUATE"):
                self.assertIn(mod, body, (v, mod))
            for score in ("GCS", "FS", "RCS", "ICS", "ARS", "HFS"):
                self.assertIn(">%s<" % score, body, (v, score))
            for cls in re.findall(r'class="([^"]*)"', body):
                self.assertFalse({"node", "edge", "dash", "particle", "hl"} & set(cls.split()), (v, cls))
            self.assertNotRegex(body, r"<animate|[Vv]alidat")
        cards = re.findall(r'<article class="card"[^>]*>', sec)
        self.assertEqual(len(cards), 4)  # the four capability groups
        for card in cards:
            self.assertIn("data-claims=", card)
        js = re.search(r'MAFig\.register\("modules".*?<!-- figjs:modules:end -->', self._script("figjs"), flags=re.S)
        self.assertTrue(js)
        self.assertRegex(js.group(0), r"\{scrub: true\}\);\s*<!-- figjs:modules:end -->")
        self.assertIn('closest("section").querySelectorAll(".cards .card")', js.group(0))  # group cards stagger in

    def test_fig_literature(self):
        self.assertEqual(EXPECTED_SECTIONS.index("literature"), EXPECTED_SECTIONS.index("modules") + 1)
        sec = re.search(r'<section id="literature".*?</section>', PAGE, flags=re.S).group(0)
        self.assertIn("<h2>Reads the literature</h2>", sec)
        fig = re.search(r'<figure class="fig" data-fig="literature" data-engine="gsap">.*?</figure>', sec, flags=re.S)
        self.assertTrue(fig)
        fig = fig.group(0)
        for v in ("wide", "narrow"):
            m = re.search(r'<svg class="sch %s"[^>]*>(.*?)</svg>' % v, fig, flags=re.S)
            self.assertTrue(m, v)
            label = re.search(r'aria-label="([^"]*)"', re.search(r'<svg class="sch %s"[^>]*>' % v, fig).group(0))
            self.assertTrue(label and len(label.group(1)) >= 20, v)
            for word in ("BM25", "page images", "graph neural network", "[p. N]"):
                self.assertIn(word, label.group(1), (v, word))
            body = m.group(1)
            self.assertIn('class="legend"', body, v)
            self.assertIn("values are illustrative", body, v)  # BM25 scores are illustrative
            self.assertEqual(body.count('class="panel'), 1, v)  # one dark focal panel: the language model
            for part in ("f-literature-beam", "f-literature-bar", "f-literature-lens", "f-literature-hop", "f-literature-answer"):
                self.assertIn(part, body, (v, part))
            for cls in re.findall(r'class="([^"]*)"', body):
                self.assertFalse({"node", "edge", "dash", "particle", "hl"} & set(cls.split()), (v, cls))
            self.assertNotRegex(body, r"<animate|[Vv]alidat|opt-in")
        import html
        flat = re.sub(r"[\u2010-\u2013]", "-", html.unescape(sec)).replace("\u2060", "")  # non-breaking hyphens too
        self.assertNotRegex(flat, r"(?i)opt-in")  # page images are read by default (C47, C53)
        cards = re.findall(r'<article class="card"[^>]*>', sec)
        self.assertEqual(len(cards), 6)  # papers, text, page images, knowledge graph, knowledge base, Deep Research
        for card in cards:
            self.assertIn("data-claims=", card)
        for cid in ("C47", "C49", "C53"):
            self.assertIn(cid, " ".join(cards))
        js = re.search(r'MAFig\.register\("literature".*?<!-- figjs:literature:end -->', self._script("figjs"), flags=re.S)
        self.assertTrue(js)
        self.assertNotIn("scrub", js.group(0))
        self.assertIn("loop", js.group(0))

    def test_fig_gaps(self):
        self.assertEqual(EXPECTED_SECTIONS.index("gaps"), EXPECTED_SECTIONS.index("literature") + 1)
        sec = re.search(r'<section id="gaps".*?</section>', PAGE, flags=re.S).group(0)
        self.assertIn("<h2>Finds what is missing</h2>", sec)
        fig = re.search(r'<figure class="fig" data-fig="gaps" data-engine="gsap">.*?</figure>', sec, flags=re.S)
        self.assertTrue(fig)
        fig = fig.group(0)
        for v in ("wide", "narrow"):
            m = re.search(r'<svg class="sch %s"[^>]*>(.*?)</svg>' % v, fig, flags=re.S)
            self.assertTrue(m, v)
            label = re.search(r'aria-label="([^"]*)"', re.search(r'<svg class="sch %s"[^>]*>' % v, fig).group(0))
            self.assertTrue(label and len(label.group(1)) >= 20, v)
            for word in ("GAR 2.1", "quote", "closure score", "LCA 5.1", "consensus", "contradiction", "not compared"):
                self.assertIn(word, label.group(1), (v, word))
            body = m.group(1)
            self.assertIn('class="legend"', body, v)
            self.assertIn("values are illustrative", body, v)  # closure score, gaps and values are illustrative
            self.assertEqual(body.count('class="panel'), 1, v)  # one dark focal panel: the closure judge
            for part in ("f-gaps-cell", "f-gaps-quote", "f-gaps-paper", "f-gaps-odo", "f-gaps-brk", "f-gaps-band"):
                self.assertIn(part, body, (v, part))
            for cls in re.findall(r'class="([^"]*)"', body):
                self.assertFalse({"node", "edge", "dash", "particle", "hl"} & set(cls.split()), (v, cls))
            self.assertNotRegex(body, r"<animate|[Vv]alidat|temperature 0")
            shown = " ".join(re.findall(r"<text[^>]*>(.*?)</text>", body, flags=re.S))
            self.assertIn("not checked", shown, v)  # the quote is not checked against the abstract (C07)
            self.assertIn("against the abstract", shown, v)
            self.assertIn("not compared", shown, v)  # pairs whose units differ (C10)
        self.assertNotIn("temperature 0", sec)  # a primed tier route sets the judge's temperature (C07)
        cards = re.findall(r'<article class="card"[^>]*>', sec)
        self.assertEqual(len(cards), 3)  # gaps by rules, closure judged against papers, where sources disagree
        for card in cards:
            self.assertIn("data-claims=", card)
        js = re.search(r'MAFig\.register\("gaps".*?<!-- figjs:gaps:end -->', self._script("figjs"), flags=re.S)
        self.assertTrue(js)
        self.assertNotIn("scrub", js.group(0))
        self.assertIn("loop", js.group(0))

    def test_fig_hypotheses(self):
        self.assertEqual(EXPECTED_SECTIONS.index("hypotheses"), EXPECTED_SECTIONS.index("gaps") + 1)
        sec = re.search(r'<section id="hypotheses".*?</section>', PAGE, flags=re.S).group(0)
        self.assertIn("<h2>Formulates hypotheses</h2>", sec)
        fig = re.search(r'<figure class="fig" data-fig="hypotheses" data-engine="gsap">.*?</figure>', sec, flags=re.S)
        self.assertTrue(fig)
        fig = fig.group(0)
        for v in ("wide", "narrow"):
            m = re.search(r'<svg class="sch %s"[^>]*>(.*?)</svg>' % v, fig, flags=re.S)
            self.assertTrue(m, v)
            label = re.search(r'aria-label="([^"]*)"', re.search(r'<svg class="sch %s"[^>]*>' % v, fig).group(0))
            self.assertTrue(label and len(label.group(1)) >= 20, v)
            for word in ("seven", "hard check", "quote", "both presentation orders", "Bradley–Terry", "bootstrap"):
                self.assertIn(word, label.group(1), (v, word))
            body = m.group(1)
            self.assertIn('class="legend"', body, v)
            self.assertIn("values are illustrative", body, v)  # entrants, games and strengths are illustrative
            self.assertEqual(body.count('class="panel'), 1, v)  # one dark focal panel: the reviewing language model
            self.assertEqual(body.count('class="card f-hypotheses-gen"'), 7, v)  # all seven generators (C56)
            self.assertLessEqual(body.count('class="f-hypotheses-pt"'), 60, v)  # swarm budget
            for part in ("f-hypotheses-funnel", "f-hypotheses-tray", "f-hypotheses-lens", "f-hypotheses-game",
                         "f-hypotheses-bar", "f-hypotheses-ci"):
                self.assertIn(part, body, (v, part))
            for cls in re.findall(r'class="([^"]*)"', body):
                self.assertFalse({"node", "edge", "dash", "particle", "hl"} & set(cls.split()), (v, cls))
            self.assertNotRegex(body, r"<animate|[Vv]alidat")
        self.assertNotIn("Up to four generators", sec)
        cards = re.findall(r'<article class="card"[^>]*>', sec)
        self.assertEqual(len(cards), 6)
        for card in cards:
            self.assertIn("data-claims=", card)
        self.assertIn("C56", " ".join(cards))  # the seven-generator card (assumed)
        js = re.search(r'MAFig\.register\("hypotheses".*?<!-- figjs:hypotheses:end -->', self._script("figjs"), flags=re.S)
        self.assertTrue(js)
        self.assertNotIn("scrub", js.group(0))
        self.assertIn("loop", js.group(0))

    def test_fig_planning(self):
        import html
        self.assertEqual(EXPECTED_SECTIONS.index("planning"), EXPECTED_SECTIONS.index("hypotheses") + 1)
        sec = re.search(r'<section id="planning".*?</section>', PAGE, flags=re.S).group(0)
        self.assertIn("<h2>Drafts computational study designs</h2>", sec)
        fig = re.search(r'<figure class="fig" data-fig="planning" data-engine="gsap">.*?</figure>', sec, flags=re.S)
        self.assertTrue(fig)
        fig = fig.group(0)
        for v in ("wide", "narrow"):
            m = re.search(r'<svg class="sch %s"[^>]*>(.*?)</svg>' % v, fig, flags=re.S)
            self.assertTrue(m, v)
            label = re.search(r'aria-label="([^"]*)"', re.search(r'<svg class="sch %s"[^>]*>' % v, fig).group(0))
            self.assertTrue(label and len(label.group(1)) >= 20, v)
            for word in ("CDTP 3.1", "CDTP 3.2", "CDTP 3.3", "3–6 steps", "1–200,000", "own estimate", "template",
                         "suggested parameters", "FS", "resources and tools", "illustrative"):
                self.assertIn(word, label.group(1), (v, word))
            body = m.group(1)
            self.assertIn('class="legend"', body, v)
            self.assertIn("values are illustrative", body, v)  # core-hours and the FS value are illustrative
            self.assertEqual(body.count('class="panel'), 1, v)  # one dark focal panel: the study designer
            self.assertEqual(body.count('class="f-planning-row'), 6, v)  # six drafted steps, the most kept (C20)
            for part in ("f-planning-bar", "f-planning-ok", "f-planning-x", "f-planning-strike", "f-planning-needle",
                         "f-planning-stamp", "f-planning-odo"):
                self.assertIn(part, body, (v, part))
            for cls in re.findall(r'class="([^"]*)"', body):
                self.assertFalse({"node", "edge", "dash", "particle", "hl"} & set(cls.split()), (v, cls))
            self.assertNotRegex(body, r"<animate|[Vv]alidat")
            shown = html.unescape(" ".join(re.findall(r"<text[^>]*>(.*?)</text>", body, flags=re.S)))
            for want in ("RULE-BASED TEMPLATE", "CDTP 3.3", "own estimate", "run's own output"):
                self.assertIn(want, shown, (v, want))
        cards = re.findall(r'<article class="card"[^>]*>', sec)
        self.assertEqual(len(cards), 4)
        for card in cards:
            self.assertIn("data-claims=", card)
        self.assertIn("C58", " ".join(cards))  # suggested parameters (assumed)
        self.assertIn("C45", " ".join(cards))  # FS as a resources-and-tools assessment (assumed)
        js = re.search(r'MAFig\.register\("planning".*?<!-- figjs:planning:end -->', self._script("figjs"), flags=re.S)
        self.assertTrue(js)
        self.assertNotIn("scrub", js.group(0))
        self.assertIn("loop", js.group(0))

    def test_fig_vasp(self):
        import html
        self.assertEqual(EXPECTED_SECTIONS.index("vasp"), EXPECTED_SECTIONS.index("planning") + 1)
        sec = re.search(r'<section id="vasp".*?</section>', PAGE, flags=re.S)
        self.assertTrue(sec)
        sec = sec.group(0)
        self.assertIn("<h2>Prepares and runs VASP workflows</h2>", sec)
        self.assertIn('<p class="kicker">07</p>', sec)
        fig = re.search(r'<figure class="fig" data-fig="vasp" data-engine="gsap">.*?</figure>', sec, flags=re.S)
        self.assertTrue(fig)
        fig = fig.group(0)
        for v in ("wide", "narrow"):
            m = re.search(r'<svg class="sch %s"[^>]*>(.*?)</svg>' % v, fig, flags=re.S)
            self.assertTrue(m, v)
            label = re.search(r'aria-label="([^"]*)"', re.search(r'<svg class="sch %s"[^>]*>' % v, fig).group(0))
            self.assertTrue(label and len(label.group(1)) >= 20, v)
            for word in ("INCAR", "POSCAR", "KPOINTS", "POTCAR", "approval", "PENDING", "RUNNING", "COMPLETED",
                         "NEB", "Birch–Murnaghan", "DOS", "illustrative"):
                self.assertIn(word, label.group(1), (v, word))
            body = m.group(1)
            self.assertIn('class="legend"', body, v)
            self.assertIn("values are illustrative", body, v)
            self.assertEqual(body.count('class="panel'), 1, v)  # one dark focal panel: the cluster
            self.assertEqual(body.count('class="f-vasp-tok'), 3, v)  # one job per step of the adsorption run
            self.assertEqual(body.count('class="f-vasp-bead'), 7, v)  # NEB: end points and five images
            self.assertEqual(body.count('class="f-vasp-ept'), 7, v)  # EOS points
            for part in ("f-vasp-gate", "f-vasp-fit", "f-vasp-dos", "f-vasp-ads"):
                self.assertIn(part, body, (v, part))
            for cls in re.findall(r'class="([^"]*)"', body):
                self.assertFalse({"node", "edge", "dash", "particle", "hl"} & set(cls.split()), (v, cls))
            self.assertNotRegex(body, r"<animate|[Vv]alidat")
            self.assertNotIn("{", body)  # the SVG has no braces: catches an uninterpolated f-string placeholder
            shown = html.unescape(" ".join(re.findall(r"<text[^>]*>(.*?)</text>", body, flags=re.S)))
            for want in ("INCAR", "POSCAR", "KPOINTS", "POTCAR", "PENDING", "RUNNING", "COMPLETED", "Approve",
                         "Birch–Murnaghan", "OUTCAR", "DOSCAR"):
                self.assertIn(want, shown, (v, want))
            # units carry a narrow no-break space (per text element: an axis tick and its unit are separate)
            for t in re.findall(r"<text[^>]*>(.*?)</text>", body, flags=re.S):
                self.assertNotRegex(html.unescape(t), r"\d[ \u00a0](eV|Å|GPa)(?![A-Za-z])")
        cards = re.findall(r'<article class="card"[^>]*>', sec)
        self.assertEqual(len(cards), 4)
        for card in cards:
            self.assertIn("data-claims=", card)
        ids = " ".join(cards)
        for cid in ("C60", "C61", "C62", "C63", "C64", "C65"):
            self.assertIn(cid, ids)
        js = re.search(r'MAFig\.register\("vasp".*?<!-- figjs:vasp:end -->', self._script("figjs"), flags=re.S)
        self.assertTrue(js)
        self.assertIn("{scrub: true}", js.group(0))

    DOMAIN_CHECKS = {  # C24: domain -> its checks (tile back text)
        "Catalyst": ("composition sum", "charge balance"), "Semiconductor": ("charge balance", "radius mismatch"),
        "Polymer": ("SMILES sanitises",), "Metal": ("composition sum",), "Ceramic": ("charge balance", "radius mismatch"),
        "MOF": ("SMILES sanitises",), "Zeolite": ("IZA framework code", "Si/Al ≥ 1"), "Nanomaterial": ("charge balance",),
        "Composite": ("composition sum",), "Biomaterial": ("SMILES sanitises", "charge balance")}

    def test_fig_domains(self):
        import html
        self.assertEqual(EXPECTED_SECTIONS.index("domains"), EXPECTED_SECTIONS.index("vasp") + 1)
        sec = re.search(r'<section id="domains".*?</section>', PAGE, flags=re.S).group(0)
        self.assertIn("<h2>Ten material domains</h2>", sec)
        self.assertIn('<p class="kicker">08</p>', sec)
        fig = re.search(r'<figure class="fig" data-fig="domains" data-engine="gsap">.*?</figure>', sec, flags=re.S)
        self.assertTrue(fig)
        fig = fig.group(0)
        for v in ("wide", "narrow"):
            tag = re.search(r'<svg class="sch %s"[^>]*>' % v, fig)
            self.assertTrue(tag, v)
            self.assertIn('role="group"', tag.group(0))
            label = html.unescape(re.search(r'aria-label="([^"]*)"', tag.group(0)).group(1))
            self.assertGreaterEqual(len(label), 20)
            for word in ("RDKit", "IZA framework code", "Si/Al ≥ 1", "Löwenstein", "composition sum ≤ 101 %",
                         "charge balance", "≤ 30 %", "unknown", "reject", "rank"):
                self.assertIn(word, label, (v, word))
            body = re.search(r'<svg class="sch %s"[^>]*>(.*?)</svg>' % v, fig, flags=re.S).group(1)
            self.assertIn('class="legend"', body, v)
            self.assertEqual(body.count('class="panel'), 1, v)  # one dark focal panel: the domain profile
            tiles = re.findall(r'<g class="f-domains-tile"([^>]*)>(.*?)</g><!--/tile-->', body, flags=re.S)
            self.assertEqual(len(tiles), 10, v)
            for (attrs, inner), (name, checks) in zip(tiles, self.DOMAIN_CHECKS.items()):
                self.assertIn('tabindex="0"', attrs)
                self.assertIn('role="img"', attrs)
                self.assertIn('data-flip="0"', attrs)
                al = html.unescape(re.search(r'aria-label="([^"]*)"', attrs).group(1))
                self.assertTrue(al.startswith(name), (v, al))
                front = re.search(r'class="f-domains-face f-domains-front".*?(?=class="f-domains-face f-domains-back")', inner, flags=re.S).group(0)
                back = inner[inner.index('class="f-domains-face f-domains-back"'):]
                self.assertIn(html.escape(name), front)
                self.assertIn('href="#i-dm-', front)  # its icon
                shown = html.unescape(" ".join(re.findall(r"<text[^>]*>(.*?)</text>", back)))
                for c in checks:
                    self.assertIn(c, shown, (v, name, c))
                for other in {c for cs in self.DOMAIN_CHECKS.values() for c in cs} - set(checks):
                    self.assertNotIn(other, shown, (v, name, other))
            self.assertEqual(body.count('class="f-domains-pip"'), 15, v)  # one pip per (domain, check) pair
            for cls in re.findall(r'class="([^"]*)"', body):
                self.assertFalse({"node", "edge", "dash", "particle", "hl"} & set(cls.split()), (v, cls))
            self.assertNotRegex(body, r"<animate|[Vv]alidat")
            self.assertNotIn("{", body)
        c = css()
        # hover and keyboard focus flip a tile through CSS alone (works without GSAP); a visible focus ring
        self.assertRegex(c, r"\.f-domains-tile:is\(:hover, :focus, \[data-flip=\"1\"\]\) \.f-domains-front\s*\{[^}]*scaleX\(0\)")
        self.assertRegex(c, r"\.f-domains-tile:focus-visible \.f-domains-ring\s*\{[^}]*visibility:\s*visible")
        rm = re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?\})\s*\}", c, flags=re.S).group(1)
        self.assertRegex(rm, r"\.f-domains-face\s*\{[^}]*transition:\s*none")
        cards = re.findall(r'<article class="card"[^>]*>', sec)
        self.assertEqual(len(cards), 2)
        js = re.search(r'MAFig\.register\("domains".*?<!-- figjs:domains:end -->', self._script("figjs"), flags=re.S)
        self.assertTrue(js)
        self.assertNotIn("scrub", js.group(0))
        self.assertIn("loop", js.group(0))
        self.assertIn('"data-flip"', js.group(0))

    # (code, what it measures, method chip, run token, run output); GCS, RCS, HFS confirmed (C44, C66); FS, ICS, ARS assumed (C45, C67)
    SCORES = [("GCS", "Gap closure", "language-model judge", "GAR 2.1", "gaps, papers read"),
              ("RCS", "RAG coverage", "term-count formula", "MMR 4.2 · 4.5 · 4.8", "analysis text"),
              ("HFS", "Hypothesis formulation", "weighted sum of five", "HF 8.4", "hypothesis records"),
              ("FS", "Plan feasibility", "resources and tools", "CDTP 3.3", "returned plan"),
              ("ICS", "Ingestion completeness", "ingested ÷ expected", "KC 6.2 · 6.4", "ingested items"),
              ("ARS", "Tool readiness", "tests + security", "SE 7.2", "newly created tool")]

    def test_fig_scores(self):
        import html
        self.assertEqual(EXPECTED_SECTIONS.index("scores"), EXPECTED_SECTIONS.index("domains") + 1)
        sec = re.search(r'<section id="scores".*?</section>', PAGE, flags=re.S)
        self.assertTrue(sec)
        sec = sec.group(0)
        self.assertIn("<h2>Scores every run</h2>", sec)
        self.assertIn('<p class="kicker">09</p>', sec)
        # kickers follow the section order
        kick = re.findall(r'<section id="([^"]+)"(?:(?!</section>).)*?<p class="kicker">(\d+)</p>', PAGE, flags=re.S)
        self.assertEqual([k for _, k in kick], [f"{EXPECTED_SECTIONS.index(i) + 1:02d}" for i, _ in kick])
        cap = re.search(r"<figcaption>(.*?)</figcaption>", sec, flags=re.S).group(1)
        self.assertIn("model-assisted measures of a run's own output", html.unescape(cap))
        fig = re.search(r'<figure class="fig" data-fig="scores" data-engine="gsap">.*?</figure>', sec, flags=re.S)
        self.assertTrue(fig)
        fig = fig.group(0)
        for v in ("wide", "narrow"):
            tag = re.search(r'<svg class="sch %s"[^>]*>' % v, fig)
            self.assertTrue(tag, v)
            label = html.unescape(re.search(r'aria-label="([^"]*)"', tag.group(0)).group(1))
            self.assertGreaterEqual(len(label), 20)
            for word in ("0–100", "model-assisted", "run's own output", "illustrative", "not comparable", "word overlap"):
                self.assertIn(word, label, (v, word))
            body = re.search(r'<svg class="sch %s"[^>]*>(.*?)</svg>' % v, fig, flags=re.S).group(1)
            self.assertIn('class="legend"', body, v)
            self.assertIn("values are illustrative", body, v)
            self.assertEqual(body.count('class="panel'), 1, v)  # one dark focal panel: the instrument cluster
            gauges = re.findall(r'<g class="f-scores-gauge" data-k="(\w+)"[^>]*>(.*?)<!--/gauge-->', body, flags=re.S)
            self.assertEqual([g[0] for g in gauges], [s[0] for s in self.SCORES], v)
            for (code, inner), (_, what, how, _m, _o) in zip(gauges, self.SCORES):
                shown = html.unescape(" ".join(re.findall(r"<text[^>]*>(.*?)</text>", inner)))
                for want in (code, what, how):
                    self.assertIn(want, shown, (v, code, want))
                for part in ("f-scores-needle", "f-scores-val", "f-scores-lamp", "f-scores-read"):
                    self.assertIn(part, inner, (v, code, part))
                self.assertIn(code, re.search(r'aria-label="([^"]*)"', tag.group(0)).group(1))
            runs = re.findall(r'<g class="f-scores-run" data-k="(\w+)"[^>]*>(.*?)</g>', body, flags=re.S)
            self.assertEqual([r[0] for r in runs], [s[0] for s in self.SCORES], v)
            for (_, inner), (_c, _w, _h, mode, out) in zip(runs, self.SCORES):
                shown = html.unescape(" ".join(re.findall(r"<text[^>]*>(.*?)</text>", inner)))
                self.assertIn(mode, shown, (v, mode))
                self.assertIn(out, shown, (v, out))
            for cls in re.findall(r'class="([^"]*)"', body):
                self.assertFalse({"node", "edge", "dash", "particle", "hl"} & set(cls.split()), (v, cls))
            self.assertNotRegex(body, r"<animate|[Vv]alidat|[Aa]ccura")
            self.assertNotIn("{", body)
        self.assertRegex(css(), r"\.f-scores-[\w-]+[^{]*\{[^}]*pointer-events:\s*none")
        cards = re.findall(r'<article class="card"[^>]*>', sec)
        self.assertGreaterEqual(len(cards), 2)
        allc = " ".join(cards)
        for cid in ("C44", "C45", "C66", "C67"):
            self.assertIn(cid, allc)
        self.assertNotRegex(html.unescape(re.sub(r"<[^>]+>", " ", sec)), r"[Vv]alidat|[Aa]ccura")
        js = re.search(r'MAFig\.register\("scores".*?<!-- figjs:scores:end -->', self._script("figjs"), flags=re.S)
        self.assertTrue(js)
        self.assertNotIn("scrub", js.group(0))
        self.assertIn("loop", js.group(0))

    def test_claims_ids_unique(self):
        # parse_claims keeps the last row per ID, so a clash between sessions would pass test_claims_statuses
        p = Path(os.environ.get("CATAGENT_REPO", str(ROOT.parent / "CATAGENT"))) / "docs" / "site" / "claims.md"
        if not p.exists():
            self.skipTest("claims register (CATAGENT docs/site/claims.md) not present")
        ids = re.findall(r"^\|\s*(C\d{2,})\s*\|", p.read_text(encoding="utf-8"), flags=re.M)
        self.assertTrue(ids)
        self.assertEqual([i for i in set(ids) if ids.count(i) > 1], [])

    def test_header_cta_breakpoint(self):
        m = re.search(r"@media \(max-width: (\d+)px\) \{ \.site-header \.btn-primary \{ display: none; \} \}", css())
        self.assertTrue(m)
        self.assertGreaterEqual(int(m.group(1)), 500)

    def test_percent_thin_space(self):
        text = visible_text(PAGE)
        self.assertIsNone(re.search(r"\d[ \u00a0]%", text))
        self.assertNotIn("single-workspace", text)

    def test_copy_button(self):
        self.assertRegex(css(), r"html:not\(\.js\) \.copy\s*\{[^}]*display:\s*none")
        self.assertRegex(PAGE, r'<span[^>]*aria-live="polite"')
        script = re.findall(r"<script>(.*?)</script>", PAGE, flags=re.S)[-1]
        self.assertRegex(script, r"writeText\([^;]*\)\.then\([\s\S]*?\.catch\(|writeText\([^;]*\)\.then\(\s*function[^)]*\)[^,]*,")
        self.assertIn("Copy failed", script)

    def test_domain_wording(self):
        text = visible_text(PAGE)
        self.assertNotIn("MatPlat adapters", text)
        self.assertNotIn("CatPlat catalyst database", text)
        self.assertIn("composition sum ≤", text)


if __name__ == "__main__":
    unittest.main()
