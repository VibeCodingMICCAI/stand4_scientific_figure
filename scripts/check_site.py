"""Check generated HTML for broken local links, images, and fragment targets."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = set()
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.errors.append(f"Duplicate ID: {attrs['id']}")
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.refs.append(attrs[key])
        if tag == "img" and "alt" not in attrs:
            self.errors.append("Image missing alt attribute")


def check():
    parsed = {}
    errors = []
    for path in SITE.rglob("*.html"):
        parser = Links()
        parser.feed(path.read_text())
        parsed[path.resolve()] = parser
        errors.extend(f"{path.relative_to(SITE)}: {e}" for e in parser.errors)
    if not parsed:
        raise SystemExit("No generated HTML. Run scripts/build_site.py first.")
    for path, parser in parsed.items():
        for ref in parser.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= "index.html"
            if not target.is_relative_to(SITE.resolve()) or not target.is_file():
                errors.append(f"{path.relative_to(SITE)}: missing local resource {ref}")
            elif url.fragment and target in parsed and unquote(url.fragment) not in parsed[target].ids:
                errors.append(f"{path.relative_to(SITE)}: missing fragment {ref}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checked {len(parsed)} pages: local links, images, and fragments resolve.")


if __name__ == "__main__":
    check()
