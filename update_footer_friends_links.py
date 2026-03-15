from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FRIENDS_HTML = (
    '      <span class="footer-friends">'
    'Friends: '
    '<a href="https://besttorontodecks.com/" rel="nofollow noopener noreferrer" target="_blank">besttorontodecks.com</a>'
    ' <span aria-hidden="true">·</span> '
    '<a href="https://npak.ca/" rel="nofollow noopener noreferrer" target="_blank">npak.ca</a>'
    ' <span aria-hidden="true">·</span> '
    '<a href="https://amaxtattoo.com/" rel="nofollow noopener noreferrer" target="_blank">amaxtattoo.com</a>'
    '</span>'
)

FOOTER_EMAIL_RE = re.compile(
    r"\n\s*<a\s+[^>]*class=\"footer-email\"[^>]*>.*?</a>\s*\n",
    flags=re.IGNORECASE | re.DOTALL,
)

FOOTER_BAR_RE = re.compile(
    r"(<div\s+class=\"footer-bar\"\s*>)(.*?)(</div>)",
    flags=re.IGNORECASE | re.DOTALL,
)


def iter_html_files() -> list[Path]:
    return sorted([p for p in ROOT.rglob("*.html") if p.is_file()])


def update_html(html: str) -> tuple[str, bool]:
    if "<footer" not in html or "site-footer" not in html:
        return html, False

    changed = False

    # Remove footer email (only the footer one has class footer-email)
    new_html, n = FOOTER_EMAIL_RE.subn("\n", html)
    if n:
        html = new_html
        changed = True

    # Insert friends links in footer bar
    if "footer-friends" not in html:
        m = FOOTER_BAR_RE.search(html)
        if m:
            before, inner, after = m.group(1), m.group(2), m.group(3)
            # Keep existing indentation pattern: footer-bar usually contains 2 spans.
            inner_stripped = inner.rstrip()
            if inner_stripped and not inner_stripped.endswith("\n"):
                inner_stripped += "\n"
            # Insert before closing div with a newline + same indentation as other spans
            replacement = before + inner_stripped + FRIENDS_HTML + "\n    " + after
            html = html[: m.start()] + replacement + html[m.end() :]
            changed = True

    return html, changed


def main() -> int:
    updated = 0
    scanned = 0
    for path in iter_html_files():
        scanned += 1
        original = path.read_text(encoding="utf-8", errors="ignore")
        new, changed = update_html(original)
        if changed:
            path.write_text(new, encoding="utf-8")
            updated += 1

    print("=== update_footer_friends_links ===")
    print(f"Root: {ROOT}")
    print(f"HTML scanned: {scanned}")
    print(f"HTML updated: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
