"""Sitewide rewrite: apex URL -> www URL.

Rationale: the server (Vercel) treats www.amaximumconstruction.com as the
canonical host and 307-redirects apex to www. All <link rel="canonical">,
og:url, twitter:url, JSON-LD url/item/image/logo, and sitemap <loc> entries
currently point to the apex. Google sees canonical -> redirect chain and
flags the page in URL Inspection.

This script rewrites every literal occurrence of `https://amaximumconstruction.com`
(not followed by another letter/digit, so we don't touch unrelated tokens)
to `https://www.amaximumconstruction.com`. UTF-8 safe per repo policy.

Skipped:
  - .venv, node_modules, .git
  - citations/ folder (off-site materials should keep apex if the user wants
    to display the cleaner brand URL on external profiles; we leave that
    decision to the user).
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKIP_DIRS = {".venv", "node_modules", ".git", "__pycache__"}
SKIP_TOPLEVEL_DIRS = {"citations"}
EXTS = {".html", ".xml", ".txt", ".json"}

# Match the apex literally, but only when NOT immediately preceded by `www.`
# and NOT followed by another domain-name character (so we don't damage
# something like `amaximumconstruction.community`).
APEX_RE = re.compile(
    r"(?<!www\.)https://amaximumconstruction\.com(?![A-Za-z0-9\-])"
)
REPLACEMENT = "https://www.amaximumconstruction.com"


def should_skip(p: Path) -> bool:
    parts = set(p.parts)
    if parts & SKIP_DIRS:
        return True
    try:
        rel = p.relative_to(ROOT)
    except ValueError:
        return True
    if rel.parts and rel.parts[0] in SKIP_TOPLEVEL_DIRS:
        return True
    return False


def process(path: Path) -> int:
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        print(f"[skip non-utf8] {path}")
        return 0
    new_text, n = APEX_RE.subn(REPLACEMENT, text)
    if n and new_text != text:
        path.write_bytes(new_text.encode("utf-8"))
        print(f"[{n:>4}] {path.relative_to(ROOT)}")
    return n


def main() -> None:
    total_files = 0
    total_fixes = 0
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in EXTS:
            continue
        if should_skip(path):
            continue
        n = process(path)
        if n:
            total_files += 1
            total_fixes += n
    print()
    print(f"Files changed: {total_files}")
    print(f"Total apex -> www rewrites: {total_fixes}")


if __name__ == "__main__":
    main()
