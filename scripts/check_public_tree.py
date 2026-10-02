"""Fail closed when unreviewed files or likely private content enter this public tree."""

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    ".github/workflows/build-desktop.yml",
    ".github/workflows/check-public-tree.yml",
    ".github/workflows/test-windows-runtime.yml",
    ".gitignore",
    "CONTRIBUTING.md",
    "README.md",
    "app.py",
    "desktop.py",
    "docs/INSTALL.md",
    "docs/PACKAGING.md",
    "docs/WINDOWS_PACKAGING.md",
    "docs/architecture.md",
    "launcher.py",
    "packaging/DESKTOP.md",
    "packaging/Install Library Analysis.cmd",
    "packaging/READ ME.txt",
    "packaging/Start Library Analysis.cmd",
    "packaging/Start Library Analysis.command",
    "packaging/build.py",
    "packaging/build_desktop.py",
    "packaging/combine_mac.py",
    "packaging/smoke_runtime.py",
    "requirements-desktop.txt",
    "requirements-lock.txt",
    "requirements.txt",
    "sample_library_survey.csv",
    "scripts/check_public_tree.py",
    "static/app.js",
    "static/index.html",
    "static/styles.css",
    "tests/benchmark_models.py",
    "tests/test_alpha.py",
    "tests/test_app.py",
    "windows_cli.py",
}
PRIVATE_MARKERS = (
    re.compile(r"\b\d{4}P\d{6}\b", re.I),
    re.compile(r"\b(?:Emory|Drexel) University\b", re.I),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile("/" + "Users/" + r"|\\" + "Users" + r"\\"),
)


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, check=True, capture_output=True,
    )
    paths = {item.decode("utf-8") for item in result.stdout.split(b"\0") if item}
    errors = []
    for name in sorted(paths):
        if name not in ALLOWED:
            errors.append(f"Unreviewed path: {name}")
            continue
        path = ROOT / name
        if not path.is_file():
            continue
        data = path.read_bytes()
        if len(data) > 1_000_000:
            errors.append(f"File exceeds public text limit: {name}")
            continue
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"Non-text file needs review: {name}")
            continue
        for marker in PRIVATE_MARKERS:
            if marker.search(content):
                errors.append(f"Possible private content in {name}: {marker.pattern}")
    if errors:
        print("Public-repository check failed:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    print(f"Public-repository check passed: {len(paths)} reviewed paths.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
