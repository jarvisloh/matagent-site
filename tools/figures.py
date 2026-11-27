#!/usr/bin/env python3
"""Regenerate the figure SVGs, their GSAP builders and the shared symbols inside index.html.

Usage: python3 tools/figures.py [--check]   (--check exits 1 if index.html would change)
"""
from __future__ import annotations

import importlib
import os
import pkgutil
import re
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figkit  # noqa: E402
import figs  # noqa: E402

INDEX = Path(os.environ.get("FIGURES_INDEX") or Path(__file__).resolve().parent.parent / "index.html")
Figure = figkit.Figure  # single definition lives in figkit so figs/<id>.py never import this (possibly __main__) module


MODULES = {m.name: importlib.import_module(f"figs.{m.name}") for m in sorted(pkgutil.iter_modules(figs.__path__), key=lambda m: m.name)}
FIGURES: dict[str, Callable[[], Figure]] = {k: m.build for k, m in MODULES.items()}


def _swap(html, key, body):
    pat = re.compile(r"(<!-- %s:start -->).*?(<!-- %s:end -->)" % (re.escape(key), re.escape(key)), re.S)
    if len(pat.findall(html)) != 1:
        raise SystemExit(f"index.html needs exactly one '{key}' marker pair")
    return pat.sub(lambda m: f"{m.group(1)}{body}{m.group(2)}", html)


def render_all(html):
    html = _swap(html, "symbols", f"\n{figkit.SYMBOLS}\n")
    for fid, build in FIGURES.items():
        fig = build()
        claims = " ".join(MODULES[fid].CLAIMS)  # the register rows the figure's text and aria-label rest on
        if not claims:
            raise SystemExit(f"figs/{fid}.py needs a non-empty CLAIMS tuple")
        tag = re.compile(r'<figure class="fig" data-fig="%s" data-engine="gsap"(?: data-claims="[^"]*")?>' % re.escape(fid))
        if len(tag.findall(html)) != 1:
            raise SystemExit(f"index.html needs exactly one <figure> for '{fid}'")
        html = tag.sub(f'<figure class="fig" data-fig="{fid}" data-engine="gsap" data-claims="{claims}">', html)
        html = _swap(html, f"fig:{fid}", f"\n{fig.wide}\n{fig.narrow}\n")
        html = _swap(html, f"figjs:{fid}", f"\n{fig.js}\n")
    return html


def main(argv):
    old = INDEX.read_text(encoding="utf-8")
    new = render_all(old)
    if "--check" in argv:
        if new != old:
            print("index.html is out of date; run python3 tools/figures.py", file=sys.stderr)
            return 1
        return 0
    if new != old:
        INDEX.write_text(new, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
