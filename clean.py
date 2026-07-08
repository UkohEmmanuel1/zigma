import os
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SAFE_PATTERNS = [
    "__pycache__/",
    "*.pyc", "*.pyo",
    "*$py.class",
    "*.egg-info/",
    "*.egg",
    "*.log",
    "*.swp", "*.swo",
    "*~",
    ".DS_Store",
]

FULL_EXTRA = [
    "venv/", "env/", ".venv/",
    ".env",
    "db.sqlite3",
    "dist/", "build/",
    "media/", "staticfiles/",
    "local_settings.py",
    ".vscode/", ".idea/",
]


def clean(path: Path, patterns: list[str], full: bool, dry_run: bool):
    skipped_dirs = {(path / p).resolve() for p in [".git"]}
    if not full:
        skipped_dirs |= {(path / p).resolve() for p in ["venv", "env", ".venv"]}

    def skip(item: Path) -> bool:
        return any(skip in item.parents for skip in skipped_dirs) or item in skipped_dirs

    dirs, files = [], []
    for pattern in patterns:
        is_dir = pattern.endswith("/")
        glob_pattern = pattern.rstrip("/")
        for item in path.rglob(glob_pattern):
            item = item.resolve()
            if skip(item):
                continue
            (dirs if is_dir and item.is_dir() else files).append(item)

    for d in dirs:
        if not d.exists():
            continue
        rel = d.relative_to(path)
        if dry_run:
            print(f"  would remove dir: {rel}")
        else:
            shutil.rmtree(d, ignore_errors=True)
            print(f"  removed dir: {rel}")
    for f in files:
        if not f.exists():
            continue
        rel = f.relative_to(path)
        if dry_run:
            print(f"  would remove file: {rel}")
        else:
            f.unlink(missing_ok=True)
            print(f"  removed file: {rel}")


def main():
    full = "--full" in sys.argv
    dry_run = "--dry-run" in sys.argv
    label = "full" if full else "safe"

    print(f"Zigma Cleanup ({label}){' [dry-run]' if dry_run else ''}")
    print()

    clean(BASE_DIR, SAFE_PATTERNS + (FULL_EXTRA if full else []), full=full, dry_run=dry_run)

    print()
    print("Done." if not dry_run else "Dry-run complete. Run without --dry-run to apply.")


if __name__ == "__main__":
    main()
