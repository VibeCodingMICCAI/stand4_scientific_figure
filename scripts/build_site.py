"""Build a static GitHub Pages site from README.md and website/gallery.json.

Run from any directory: python scripts/build_site.py
Requires the packages listed in requirements-site.txt. Output: _site/.
"""

import json
import re
import shutil
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from string import Template

import markdown

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "website"
OUT = ROOT / "_site"
REPO = "https://github.com/VibeCodingMICCAI/stand4_scientific_figure"
ISSUE = REPO + "/issues/new?template=figure-submission.yml"


class TutorialHTML(HTMLParser):
    """Rewrite repo-local links for the site and make tables scrollable."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.output = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src"):
            value = attrs.get(key, "")
            for old, new in (("assets/", "../assets/"), ("scripts/", "../code/"),
                             ("sample-datasets/", "../data/")):
                if value.startswith(old):
                    attrs[key] = new + value[len(old):]
                    break
            if value == "WEBSITE.md":
                attrs[key] = REPO + "/blob/main/WEBSITE.md"
            if value == "https://VibeCodingMICCAI.github.io/stand4_scientific_figure/gallery/":
                attrs[key] = "../gallery/"
        if tag == "img":
            attrs["loading"] = "lazy"
            attrs["decoding"] = "async"
        if tag == "table":
            self.output.append('<div class="table-scroll" role="region" aria-label="Data table" tabindex="0">')
        formatted = " ".join(escape(k) if v is None else f'{escape(k)}="{escape(v, quote=True)}"'
                             for k, v in attrs.items())
        self.output.append(f"<{tag}{' ' if formatted else ''}{formatted}>")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        self.output.append(f"</{tag}>")
        if tag == "table":
            self.output.append("</div>")

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append(f"&{name};")

    def handle_charref(self, name):
        self.output.append(f"&#{name};")


def local_url(path):
    if path.startswith("assets/"):
        return "../" + path
    if path.startswith("scripts/"):
        return "../code/" + path.removeprefix("scripts/")
    return "../data/" + path.removeprefix("sample-datasets/")


def card(entry):
    def e(key):
        return escape(entry[key], quote=True)

    data_links = ""
    for index, key in enumerate(("data", "extra_data")):
        if entry.get(key):
            label = "Data" if index == 0 else "32B data"
            data_links += f'<a href="{escape(local_url(entry[key]))}">{label} ↓</a>'
    search_text = escape(" ".join(str(v) for v in entry.values() if v), quote=True)
    return f'''
<article class="figure-card" id="{e('id')}" data-category="{e('category')}" data-search="{search_text}">
  <div class="card-image"><a class="image-zoom" href="{local_url(entry['image'])}" aria-label="Enlarge: {e('title')}"><img src="{local_url(entry['image'])}" alt="{e('image_alt')}" loading="lazy" decoding="async"></a><span class="image-hint">Click to enlarge ↗</span></div>
  <div class="card-body">
    <div class="card-tags"><span class="category-tag">{e('category')}</span><span>{e('type')}</span></div>
    <h2>{e('title')}</h2><p class="card-lesson">{e('lesson')}</p>
    <p class="card-citation">{e('citation')}</p>
    <div class="card-links"><a href="{e('paper_url')}">Paper ↗</a><a href="{local_url(entry['code'])}">Code ↓</a>{data_links}</div>
    <details class="card-details"><summary>Reference, run instructions &amp; design notes</summary>
      <p class="source-title">{e('paper')}</p><p>{e('panel')}</p>
      <p class="detail-label">{e('reference_label')}</p>
      <a class="image-zoom" href="{local_url(entry['reference_image'])}" aria-label="Enlarge reference for {e('title')}"><img src="{local_url(entry['reference_image'])}" alt="{e('reference_label')}: {e('paper')}" loading="lazy" decoding="async"></a>
      <p class="detail-label">Data &amp; interpretation</p><p>{e('note')}</p>
      <p class="detail-label">Run from the repository root</p><pre><code>{e('command')}</code></pre><p>{e('dependencies')}</p>
      <p class="credit">{e('credit')}</p>
    </details>
  </div>
</article>'''


def page(name, content, title, description, prefix=""):
    viewer = '''<dialog id="figure-viewer" class="figure-viewer" aria-label="Full-size scientific figure"><button type="button" class="viewer-close" autofocus>Close ×</button><img alt=""><p class="viewer-caption"></p></dialog>'''
    template = Template((SOURCE / "base.html").read_text())
    result = template.substitute(
        content=content, title=escape(title), description=escape(description),
        prefix=prefix, page_class=name, repo_url=REPO, issue_url=ISSUE,
        tutorial_current='aria-current="page"' if name == "tutorial" else "",
        gallery_current='aria-current="page"' if name == "gallery" else "",
        lightbox=viewer if name != "tutorial" else "",
    )
    destination = OUT / ("index.html" if name == "home" else f"{name}/index.html")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(result)


def build():
    entries = json.loads((SOURCE / "gallery.json").read_text())
    if len({entry["id"] for entry in entries}) != len(entries):
        raise ValueError("Gallery IDs must be unique")
    for entry in entries:
        if not re.fullmatch(r"[a-z0-9-]+", entry["id"]):
            raise ValueError(f"Invalid gallery ID: {entry['id']}")
        for key in ("image", "reference_image", "code", "data", "extra_data"):
            if entry.get(key) and not (ROOT / entry[key]).is_file():
                raise FileNotFoundError(entry[key])
    OUT.mkdir(exist_ok=True)
    for directory, target in (("assets", "assets"), ("scripts", "code"), ("sample-datasets", "data")):
        destination = OUT / target
        destination.mkdir(exist_ok=True)
        # Copy files only; do not package caches or environments in the site.
        for file in (ROOT / directory).iterdir():
            if file.is_file() and not file.name.startswith("."):
                shutil.copy2(file, destination / file.name)
    for filename in ("styles.css", "site.js", "favicon.svg"):
        shutil.copy2(SOURCE / filename, OUT / filename)
    (OUT / ".nojekyll").write_text("")

    home = Template((SOURCE / "home.html").read_text()).substitute(issue_url=ISSUE)
    home = home.replace("4 starter examples", f"{len(entries)} starter examples")
    page("home", home, "Scientific figures, thoughtfully made",
         "A MICCAI tutorial and community gallery for generating, refining, and reproducing scientific figures with AI coding assistants.")

    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "md_in_html"],
                           extension_configs={"toc": {"toc_depth": "2", "permalink": True,
                                                      "permalink_class": "heading-link"}})
    readme = (ROOT / "README.md").read_text().replace("<details>", '<details markdown="1">')
    rendered = md.convert(readme)
    parser = TutorialHTML()
    parser.feed(rendered)
    toc = "".join(f'<li><a href="#{escape(item["id"])}">{escape(item["name"])}</a></li>'
                  for item in md.toc_tokens[0].get("children", []))
    tutorial = f'''<div class="tutorial-layout page-width"><aside class="tutorial-sidebar"><p class="eyebrow">In this tutorial</p><nav aria-label="Tutorial contents"><ul>{toc}</ul></nav><p class="sidebar-source"><a href="{REPO}/blob/main/README.md">View the README on GitHub ↗</a></p></aside><article class="tutorial-content">{''.join(parser.output)}</article></div>'''
    page("tutorial", tutorial, "The tutorial", "Dataset figures, results plots, and method diagrams: practical examples and prompts for scientific figure generation.", "../")

    gallery = Template((SOURCE / "gallery.html").read_text()).substitute(
        issue_url=ISSUE, cards="\n".join(card(entry) for entry in entries))
    gallery = gallery.replace("4 examples", f"{len(entries)} examples")
    page("gallery", gallery, "The gallery", "Reference figures alongside adaptations, reproductions, plotting code, and design lessons. Submit your own example through GitHub Issues.", "../")
    print(f"Built home, tutorial, and gallery ({len(entries)} examples) in {OUT}")


if __name__ == "__main__":
    build()
