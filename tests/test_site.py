import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "index.html").read_text(encoding="utf-8") if (ROOT / "index.html").exists() else ""

EXPECTED_SECTIONS = ["opening", "literature"]  # tasks 4-7 append
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
        for url in re.findall(r'(?:src|href)="(https?://[^"]+)"', PAGE):
            self.assertIn(re.match(r"https?://([^/]+)", url).group(1),
                          {"fonts.googleapis.com", "fonts.gstatic.com"}, url)

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
        repo = "/Users/jarvisloh/PycharmProjects/CATAGENT"
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

    def test_reduced_motion_covers_rejected_edges(self):
        m = re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?\})\s*\}", css(), flags=re.S)
        self.assertIn(".sch .edge.rej", m.group(1))

    def test_sections_in_order(self):
        ids = re.findall(r'<section[^>]*\bid="([^"]+)"', PAGE)
        self.assertEqual(ids[:len(EXPECTED_SECTIONS)], EXPECTED_SECTIONS)

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

    def test_cards_have_claims(self):
        known = claims()
        for tag in re.findall(r'<article class="card"[^>]*>', PAGE):
            m = re.search(r'data-claims="([^"]+)"', tag)
            self.assertTrue(m, tag)
            for cid in m.group(1).split():
                self.assertIn(known.get(cid), ("confirmed", "changed"), cid)


if __name__ == "__main__":
    unittest.main()
