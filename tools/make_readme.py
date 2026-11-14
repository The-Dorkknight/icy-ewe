#!/usr/bin/env python3
# Required Notice: Copyright Matthew Armstrong (https://github.com/The-Dorkknight)
# Licensed under the PolyForm Noncommercial License 1.0.0. No warranty.
"""Make README.md the whole paper (GitHub won't show a PDF inside a README).
Generated from paper/paper.md: edit the paper, then run  python3 tools/make_readme.py"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = "paper/icy-ewe-v1.1.pdf"
PAGES = "https://the-dorkknight.github.io/icy-ewe/"


def slug(text):
    s = re.sub(r"[^\w\- ]", "", text.strip().lower())
    return s.replace(" ", "-")


def main():
    src = open(os.path.join(ROOT, "paper", "paper.md"), encoding="utf-8").read()
    meta, body = re.match(r"---\n(.*?)\n---\n(.*)", src, re.S).groups()
    m = dict(re.findall(r'^(\w+):\s*"(.*)"$', meta, re.M))
    body = body.replace("](figures/", "](paper/figures/")

    def figure(mo):
        cap, path = mo.group(1), mo.group(2)
        return (f'<p align="center"><img src="{path}" width="88%" alt=""></p>\n\n'
                f'<p align="center"><sub>{md_inline(cap)}</sub></p>')
    body = re.sub(r"^!\[(.*?)\]\((paper/figures/[^)]+)\)$", figure, body, flags=re.M)
    body = re.sub(r"\^([^^\s]+)\^", r"<sup>\1</sup>", body)          # pandoc superscripts
    heads = re.findall(r"^# (.+)$", body, re.M)
    toc = "\n".join(f"- [{h}](#{slug(h)})" for h in heads)
    top = (f"<!-- GENERATED from paper/paper.md by tools/make_readme.py. Edit the paper, then run the tool. -->\n"
           f"# {m['title']}\n\n**{m['subtitle']}**\n\n{m['author']} · {m['date']}\n\n"
           f"📄 **[PDF]({PDF})** · 🌐 **[Web page]({PAGES})** · 🛠️ **[The app: Scantastic]"
           f"(https://github.com/The-Dorkknight/scantastic)** · 📚 **Cite:** [CITATION.cff](CITATION.cff)\n\n"
           f"**Contents**\n\n{toc}\n\n---\n")
    about = """
---

## About this repository

| Path | What |
|---|---|
| [`paper/paper.md`](paper/paper.md) | The paper (Markdown) |
| [`paper/icy-ewe-v1.1.pdf`](paper/icy-ewe-v1.1.pdf) | The paper as a PDF |
| [`paper/figures/`](paper/figures/) | Every figure: real photos, app screenshots from made-up data, and drawings |
| [`index.html`](index.html) | The web version, for GitHub Pages (it uses `paper/figures`) |
| [`tools/`](tools/) | `make_figures.py` redraws the drawings, `take_screenshots.py` retakes the app screenshots (needs the Scantastic app beside it), `build_paper.py` builds the PDF and web page, `make_readme.py` builds this README |

To rebuild: `python3 tools/make_figures.py paper/figures` (numpy, matplotlib, OpenCV), then
`python3 tools/build_paper.py` (pandoc, Node with Playwright's Chromium), then `python3 tools/make_readme.py`.

**Join in:** run the test plan (section 8), post results with photos as an issue or discussion, or point out prior art
I missed. Everyone who contributes gets credited in the next version.

**Licence:** paper text and figures [CC BY-SA 4.0](LICENSE.md); scripts in `tools/`
[PolyForm Noncommercial 1.0.0](LICENSE-CODE.md) (source-available, not open source); the methods in section 9 are
dedicated to the public as a defensive publication. Not legal advice. Not affiliated with Intel, Prowise or anyone else
named in the paper.
"""
    out = top + body.rstrip() + "\n" + about
    open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(out)
    print("README.md:", len(heads), "sections,", body.count("<img "), "figures")


def md_inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<i>\1</i>", s)


if __name__ == "__main__":
    main()
