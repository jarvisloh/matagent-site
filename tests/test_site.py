import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "index.html").read_text(encoding="utf-8") if (ROOT / "index.html").exists() else ""

EXPECTED_SECTIONS = ["opening", "literature", "gaps", "hypotheses", "planning", "domains", "record", "improvement", "interfaces", "contact"]
FORBIDDEN = [r"\bautonomous", r"self-driving", r"closed[- ]loop", r"discover(s|ed|ing)? new materials",
  r"\bvalidated\b", r"runs? (dft )?simulations", r"\bGNN", r"33 sub-modes", r"\b(ICS|ARS|FS)\b",
  r"recall@\d\s*(=|:|of)", r"win rate", r"hits@", r"\bMRR\b", r"bayesian optimi[sz]", r"active learning",
  r"surrogate", r"uncertainty quantification", r"\bslurm\b", r"\bHPC\b", r"reflexion", r"local (llm|model)s?",
  r"structure generation", r"send to maestro", r"equation[- ]of[- ]state fit", r"birch", r"\bNEB\b",
  r"slab generation", r"submits? (the )?jobs?", r"job submission", r"air-gapped"]

TOKENS = {
    "light": {"bg": "#F6F8FB", "dot": "#D5DDE8", "ink": "#0B1220", "muted": "#4B5970",
              "line": "#C3CEDC", "node": "#FFFFFF", "accent": "#0E7F78", "accent-2": "#9A600E"},
    "dark": {"bg": "#0A0F1A", "dot": "#1A2538", "ink": "#E6EDF5", "muted": "#8A97AB",
             "line": "#24324A", "node": "#101A2B", "accent": "#4FD1C5", "accent-2": "#F5B544"},
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
    p = ROOT / "claims.md"
    return parse_claims(p.read_text(encoding="utf-8")) if p.exists() else {}


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
            self.assertIn('role="img"', tag)
            m = re.search(r'aria-label="([^"]*)"', tag)
            self.assertTrue(m and len(m.group(1)) >= 20, tag)

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
        self.assertTrue(tags)  # the literature figure's opt-in branch is dashed
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
        self.assertEqual(hrefs, ["literature", "gaps", "hypotheses", "planning", "domains",
                                 "record", "improvement", "interfaces"])

    def test_parse_claims(self):
        sample = ("| ID | Claim (site wording basis) | Source @bc983737 (path:lines) | Status |\n"
                  "|---|---|---|---|\n| C01 | a | x.py:1-2 | Confirmed |\n"
                  "| C02 | b | y.py:3 | CHANGED |\n| note | c | d | confirmed |\n")
        self.assertEqual(parse_claims(sample), {"C01": "confirmed", "C02": "changed"})

    def test_claims_register_complete(self):
        c = claims()
        self.assertEqual(sorted(c), [f"C{i:02d}" for i in range(1, 41)])
        for cid, status in c.items():
            self.assertIn(status, {"confirmed", "changed", "dropped"}, cid)

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
                self.assertIn(known.get(cid), ("confirmed", "changed"), cid)

    def test_idx_full_opacity(self):
        # .idx is muted text; any opacity below 1 drops it under 4.5:1
        m = re.search(r"\.sch \.idx\s*\{([^}]*)\}", css())
        self.assertTrue(m)
        op = re.search(r"opacity:\s*([\d.]+)", m.group(1))
        self.assertTrue(op is None or float(op.group(1)) >= 1, m.group(1))

    def test_sublabel_length(self):
        import html
        for svg in re.findall(r"<svg\b[^>]*class=\"sch [^\"]*\".*?</svg>", PAGE, flags=re.S):
            for t in re.findall(r'<text class="sub"[^>]*>(.*?)</text>', svg, flags=re.S):
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
        fig = re.search(r'<figure class="fig" data-fig="opening">.*?</figure>', PAGE, flags=re.S).group(0)
        shown = " ".join(re.findall(r'<text class="(?:sub|ttl)"[^>]*>(.*?)</text>', fig))
        shown += " " + re.search(r"<figcaption>(.*?)</figcaption>", fig, flags=re.S).group(1)
        self.assertNotRegex(shown, r"\b(LCA|HF|PLAN|CDTP)\b|\d\.\d|[Vv]alidation")
        self.assertRegex(fig, r'aria-label="[^"]*LCA 5\.1[^"]*HF 8\.3')

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
