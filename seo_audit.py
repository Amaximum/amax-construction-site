import os
import re
from collections import Counter, defaultdict


ROOT = os.path.dirname(os.path.abspath(__file__))


HTML_EXT = ".html"


SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
}


def iter_html_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            if name.lower().endswith(HTML_EXT):
                yield os.path.join(dirpath, name)


TITLE_RE = re.compile(r"<title\b[^>]*>.*?</title>", re.IGNORECASE | re.DOTALL)
META_NAME_RE = re.compile(
    r"<meta\b[^>]*\bname\s*=\s*['\"](?P<name>[^'\"]+)['\"][^>]*>",
    re.IGNORECASE,
)
LINK_CANONICAL_RE = re.compile(
    r"<link\b[^>]*\brel\s*=\s*['\"]canonical['\"][^>]*>",
    re.IGNORECASE,
)
OG_RE = re.compile(
    r"<meta\b[^>]*\bproperty\s*=\s*['\"]og:[^'\"]+['\"][^>]*>",
    re.IGNORECASE,
)
LD_JSON_RE = re.compile(
    r"<script\b[^>]*\btype\s*=\s*['\"]application/ld\+json['\"][^>]*>",
    re.IGNORECASE,
)
SCRIPT_SRC_RE = re.compile(
    r"<script\b[^>]*\bsrc\s*=\s*['\"](?P<src>[^'\"]+)['\"][^>]*>",
    re.IGNORECASE,
)
CSS_HREF_RE = re.compile(
    r"<link\b[^>]*\brel\s*=\s*['\"]stylesheet['\"][^>]*\bhref\s*=\s*['\"](?P<href>[^'\"]+)['\"][^>]*>",
    re.IGNORECASE,
)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def main() -> int:
    files = list(iter_html_files(ROOT))
    files.sort()

    missing = defaultdict(list)
    scripts_dupe = []
    css_dupe = []
    external_script_counter = Counter()

    for path in files:
        html = read_text(path)

        if not TITLE_RE.search(html):
            missing["title"].append(rel(path))

        meta_names = {m.group("name").strip().lower() for m in META_NAME_RE.finditer(html)}
        if "description" not in meta_names:
            missing["meta_description"].append(rel(path))
        if "viewport" not in meta_names:
            missing["viewport"].append(rel(path))
        if "robots" not in meta_names:
            missing["robots_meta"].append(rel(path))
        if not LINK_CANONICAL_RE.search(html):
            missing["canonical"].append(rel(path))

        if not OG_RE.search(html):
            missing["open_graph"].append(rel(path))

        if not LD_JSON_RE.search(html):
            missing["schema_ld_json"].append(rel(path))

        scripts = [m.group("src").strip() for m in SCRIPT_SRC_RE.finditer(html)]
        styles = [m.group("href").strip() for m in CSS_HREF_RE.finditer(html)]

        dup_scripts = [src for src, c in Counter(scripts).items() if c > 1]
        if dup_scripts:
            scripts_dupe.append((rel(path), dup_scripts))

        dup_css = [href for href, c in Counter(styles).items() if c > 1]
        if dup_css:
            css_dupe.append((rel(path), dup_css))

        for src in scripts:
            if src.startswith("http://") or src.startswith("https://"):
                external_script_counter[src] += 1

    def summarize(key: str) -> str:
        items = missing.get(key, [])
        if not items:
            return f"{key}: OK"
        sample = ", ".join(items[:8])
        more = "" if len(items) <= 8 else f" (+{len(items) - 8} more)"
        return f"{key}: MISSING on {len(items)}/{len(files)} pages — {sample}{more}"

    print(f"HTML files scanned: {len(files)}")
    print()
    for k in [
        "title",
        "meta_description",
        "canonical",
        "viewport",
        "robots_meta",
        "open_graph",
        "schema_ld_json",
    ]:
        print(summarize(k))

    print()
    if scripts_dupe:
        print(f"Duplicate script includes within a page: {len(scripts_dupe)} page(s)")
        for p, d in scripts_dupe[:10]:
            print(f"  - {p}: {d}")
        if len(scripts_dupe) > 10:
            print(f"  (+{len(scripts_dupe) - 10} more)")
    else:
        print("Duplicate script includes within a page: none")

    if css_dupe:
        print(f"Duplicate CSS includes within a page: {len(css_dupe)} page(s)")
        for p, d in css_dupe[:10]:
            print(f"  - {p}: {d}")
        if len(css_dupe) > 10:
            print(f"  (+{len(css_dupe) - 10} more)")
    else:
        print("Duplicate CSS includes within a page: none")

    print()
    if external_script_counter:
        print("Most common external scripts (top 10):")
        for src, count in external_script_counter.most_common(10):
            print(f"  - {count:>4}x {src}")
    else:
        print("External scripts: none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
