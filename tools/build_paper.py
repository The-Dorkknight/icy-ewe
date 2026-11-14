#!/usr/bin/env python3
# Required Notice: Copyright Matthew Armstrong (https://github.com/The-Dorkknight)
# Licensed under the PolyForm Noncommercial License 1.0.0. No warranty.
"""Build the paper: paper/paper.md -> index.html (the web page, using paper/figures) and
paper/icy-ewe-v1.1.pdf. Needs pandoc and Node with Playwright's Chromium.
    python3 tools/build_paper.py"""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPER = os.path.join(ROOT, "paper")
DOCS = ROOT                          # the web page is index.html at the top (GitHub Pages: main, root)
PDF = os.path.join(PAPER, "icy-ewe-v1.1.pdf")
BADGES = ["Defensive publication", "CC BY-SA 4.0", "Scantastic 0.9.0 – 0.11.0", "Made-up test data, said so"]



def html():
    body = subprocess.run(["pandoc", os.path.join(PAPER, "paper.md"), "-f", "markdown+implicit_figures",
                           "-t", "html5", "--standalone", "--wrap=none",
                           "--metadata", "lang=en", "--css", "paper.css"],
                          capture_output=True, text=True, check=True).stdout
    badges = "<div class=\"badges\">" + "".join(f"<span>{b}</span>" for b in BADGES) + "</div>"
    body = body.replace("</header>", badges + "</header>", 1)
    body = re.sub(r"<style>.*?</style>", "", body, flags=re.S)       # pandoc's default style: ours instead
    body = body.replace("<head>", "<head>\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">", 1)
    return body


def main():
    page = html()
    # figures and style stay in paper/: the page points there instead of keeping a second copy
    page = page.replace('src="figures/', 'src="paper/figures/').replace('href="paper.css"', 'href="paper/paper.css"')
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    js = """
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + process.argv[2], { waitUntil: 'networkidle' });
  await p.pdf({ path: process.argv[3], format: 'A4', printBackground: true,
    margin: { top: '14mm', bottom: '16mm', left: '13mm', right: '13mm' },
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;color:#888;width:100%;text-align:center;font-family:sans-serif">Icy Ewe v1.1 · Matthew Armstrong · CC BY-SA 4.0 · page <span class="pageNumber"></span> of <span class="totalPages"></span></div>' });
  await b.close();
})();
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as t:
        t.write(js)
    env = dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH", "") or subprocess.run(
        ["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    subprocess.run(["node", t.name, os.path.join(DOCS, "index.html"), PDF], check=True, env=env)
    os.unlink(t.name)
    print("built", os.path.relpath(PDF, ROOT), "and index.html")


if __name__ == "__main__":
    main()
