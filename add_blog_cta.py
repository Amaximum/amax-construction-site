"""
Add a second in-content BOOK NOW CTA to any HTML page that currently has
only one booking link (i.e., only the navbar BOOK NOW).

Categorization source of truth: the navbar's existing /book-*.html href.
This was already correctly assigned by prior work on Computer 1 — so we
trust it and route the in-content CTA to the same form.

Idempotent: every injection is wrapped in <!-- BLOG_CTA_INJECTED --> marker;
re-running is a no-op.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).parent
MARKER = "<!-- BLOG_CTA_INJECTED -->"

# Match any href="/book-X.html" (the 18 form pages)
HREF_RE = re.compile(r'href="(/book-[a-z]+\.html)"')

# Skip the form pages themselves, and infrastructure dirs
SKIP_DIRS = {
    "book-now", "blog", "portfolio", "locations", "services",
    "css", "js", "img", "assets", "node_modules", ".venv", ".git",
    "thank-you-page",
}


def make_cta_html(target: str) -> str:
    """Return the in-content CTA island to inject."""
    return (
        f'\n{MARKER}\n'
        f'<section class="island reveal" aria-label="Book this service" '
        f'style="text-align:center;padding:2rem 1rem;">\n'
        f'  <span class="shine" aria-hidden="true"></span>\n'
        f'  <div class="shell">\n'
        f'    <h2 style="margin-bottom:.5rem;">Ready to Get Started?</h2>\n'
        f'    <p class="muted" style="margin-bottom:1.25rem;">'
        f'Book a free consultation. We\'ll discuss your project and provide a fixed quote.</p>\n'
        f'    <a class="btn btn-primary" href="{target}" '
        f'style="display:inline-block;">Book Free Consultation &rarr;</a>\n'
        f'  </div>\n'
        f'</section>\n'
    )


def process_file(path: Path) -> str | None:
    """Process one HTML file. Returns the target form URL if injected, else None."""
    text = path.read_text(encoding="utf-8", errors="ignore")

    # Already injected?
    if MARKER in text:
        return None

    # Count current booking links
    matches = HREF_RE.findall(text)
    if len(matches) != 1:
        # Either 0 (skip — page has no booking concept) or >=2 (already OK)
        return None

    target = matches[0]
    cta = make_cta_html(target)

    # Strategy: inject before </main> (modern layout), else before <footer
    if "</main>" in text:
        new_text = text.replace("</main>", cta + "</main>", 1)
    else:
        # Fallback: inject before the first <footer
        m = re.search(r"<footer\b", text)
        if not m:
            return None
        new_text = text[: m.start()] + cta + text[m.start():]

    path.write_text(new_text, encoding="utf-8")
    return target


def main() -> None:
    injected = 0
    by_target: dict[str, int] = {}
    skipped_no_book = 0
    already_ok = 0

    for d in ROOT.iterdir():
        if not d.is_dir():
            continue
        if d.name.startswith(".") or d.name.startswith("book-") or d.name in SKIP_DIRS:
            continue
        idx = d / "index.html"
        if not idx.exists():
            continue

        text = idx.read_text(encoding="utf-8", errors="ignore")
        n = len(HREF_RE.findall(text))
        if n == 0:
            skipped_no_book += 1
            continue
        if n >= 2:
            already_ok += 1
            continue

        result = process_file(idx)
        if result:
            injected += 1
            by_target[result] = by_target.get(result, 0) + 1

    print(f"Injected CTA on {injected} pages.")
    print(f"Already had >=2 links: {already_ok}")
    print(f"Had 0 booking links (skipped): {skipped_no_book}")
    print("\nBy target form:")
    for t, c in sorted(by_target.items(), key=lambda x: -x[1]):
        print(f"  {c:4d}  {t}")


if __name__ == "__main__":
    main()
