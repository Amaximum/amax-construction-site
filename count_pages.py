import os


ROOT = os.path.dirname(os.path.abspath(__file__))


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
            if name.lower().endswith(".html"):
                yield os.path.relpath(os.path.join(dirpath, name), root).replace("\\", "/")


def main() -> int:
    files = sorted(iter_html_files(ROOT))
    total = len(files)

    blog_folder = [f for f in files if f.startswith("blog/")]
    without_blog_folder = [f for f in files if not f.startswith("blog/")]

    # More aggressive definition: any path segment containing the substring "blog".
    without_any_blog_segment = [
        f for f in files if all("blog" not in part.lower() for part in f.split("/"))
    ]

    blog_segments = sorted({part for f in files for part in f.split("/") if "blog" in part.lower()})

    print(f"Total HTML pages: {total}")
    print(f"Blog pages (under blog/): {len(blog_folder)}")
    print(f"Non-blog pages (excluding blog/): {len(without_blog_folder)}")
    print(f"Non-blog pages (excluding any path segment containing 'blog'): {len(without_any_blog_segment)}")
    if blog_segments:
        print(f"Path segments containing 'blog': {blog_segments}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
