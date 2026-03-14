import os
import re


ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://amaximumconstruction.com"
SITE_NAME = "aMaximum Construction"
LOGO_URL = f"{BASE_URL}/img/logo.png"


SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
}


TITLE_RE = re.compile(r"<title\b[^>]*>(?P<title>.*?)</title>", re.IGNORECASE | re.DOTALL)
META_DESC_RE = re.compile(
    r"<meta\b[^>]*\bname\s*=\s*['\"]description['\"][^>]*\bcontent\s*=\s*['\"](?P<content>[^'\"]*)['\"][^>]*>",
    re.IGNORECASE,
)
CANONICAL_RE = re.compile(
    r"<link\b[^>]*\brel\s*=\s*['\"]canonical['\"][^>]*\bhref\s*=\s*['\"](?P<href>[^'\"]+)['\"][^>]*>",
    re.IGNORECASE,
)
ROBOTS_META_RE = re.compile(
    r"<meta\b[^>]*\bname\s*=\s*['\"]robots['\"][^>]*>",
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
ICON_RE = re.compile(r"<link\b[^>]*\brel\s*=\s*['\"](?:icon|shortcut icon)['\"][^>]*>", re.IGNORECASE)
APPLE_ICON_RE = re.compile(r"<link\b[^>]*\brel\s*=\s*['\"]apple-touch-icon['\"][^>]*>", re.IGNORECASE)


def iter_html_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            if name.lower().endswith(".html"):
                yield os.path.join(dirpath, name)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def compute_url(rel_path: str) -> str:
    rel_path = rel_path.replace("\\", "/")
    if rel_path == "index.html":
        return f"{BASE_URL}/"
    if rel_path.endswith("/index.html"):
        return f"{BASE_URL}/" + rel_path[: -len("index.html")]
    return f"{BASE_URL}/" + rel_path


def extract_title(html: str) -> str:
    m = TITLE_RE.search(html)
    if not m:
        return SITE_NAME
    title = re.sub(r"\s+", " ", m.group("title")).strip()
    return title or SITE_NAME


def extract_description(html: str) -> str:
    m = META_DESC_RE.search(html)
    if not m:
        return ""
    return (m.group("content") or "").strip()


def ensure_before_head_close(html: str, insert_block: str) -> str:
    idx = html.lower().rfind("</head>")
    if idx == -1:
        return html
    prefix = html[:idx]
    suffix = html[idx:]
    if not prefix.endswith("\n"):
        prefix += "\n"
    return prefix + insert_block + "\n" + suffix


def main() -> int:
    changed = 0
    scanned = 0

    for path in sorted(iter_html_files(ROOT)):
        scanned += 1
        rel_path = os.path.relpath(path, ROOT)
        html = read_text(path)
        original = html

        title = extract_title(html)
        desc = extract_description(html)

        canonical = None
        m_can = CANONICAL_RE.search(html)
        if m_can:
            canonical = (m_can.group("href") or "").strip()
        if not canonical:
            canonical = compute_url(rel_path)
            html = ensure_before_head_close(
                html,
                f"  <link rel=\"canonical\" href=\"{canonical}\">",
            )

        # robots
        if not ROBOTS_META_RE.search(html):
            html = ensure_before_head_close(
                html,
                "  <meta name=\"robots\" content=\"index, follow, max-image-preview:large\">",
            )

        # favicon links
        if not ICON_RE.search(html):
            html = ensure_before_head_close(
                html,
                "  <link rel=\"icon\" href=\"/img/logo.png\" type=\"image/png\">",
            )
        if not APPLE_ICON_RE.search(html):
            html = ensure_before_head_close(
                html,
                "  <link rel=\"apple-touch-icon\" href=\"/img/logo.png\">",
            )

        # Open Graph
        if not OG_RE.search(html):
            og_lines = [
                "  <meta property=\"og:type\" content=\"website\">",
                f"  <meta property=\"og:title\" content=\"{html_escape_attr(title)}\">",
            ]
            if desc:
                og_lines.append(f"  <meta property=\"og:description\" content=\"{html_escape_attr(desc)}\">")
            og_lines.extend(
                [
                    f"  <meta property=\"og:url\" content=\"{canonical}\">",
                    f"  <meta property=\"og:site_name\" content=\"{SITE_NAME}\">",
                ]
            )
            html = ensure_before_head_close(html, "\n".join(og_lines))

        # Schema.org
        if not LD_JSON_RE.search(html):
            schema = (
                "  <script type=\"application/ld+json\">\n"
                "    {\n"
                "      \"@context\": \"https://schema.org\",\n"
                "      \"@type\": \"Organization\",\n"
                f"      \"name\": \"{SITE_NAME}\",\n"
                f"      \"url\": \"{BASE_URL}/\",\n"
                f"      \"logo\": \"{LOGO_URL}\"\n"
                "    }\n"
                "  </script>"
            )
            html = ensure_before_head_close(html, schema)

        if html != original:
            write_text(path, html)
            changed += 1

    print(f"Scanned: {scanned} HTML files")
    print(f"Changed: {changed} file(s)")
    return 0


def html_escape_attr(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


if __name__ == "__main__":
    raise SystemExit(main())
