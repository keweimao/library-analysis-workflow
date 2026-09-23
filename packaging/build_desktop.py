"""Build a native desktop bundle on the current operating system."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
VERSION = "0.2.0-alpha"


def build():
    if sys.platform not in {"darwin", "win32"}:
        raise SystemExit("Build desktop packages on macOS or Windows.")
    OUT.mkdir(exist_ok=True)
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed",
        "--onedir", "--name", "LibraryAnalysis", "--add-data",
        f"{ROOT / 'static'}{os.pathsep}static", "--distpath", str(OUT / "desktop-build"),
        "--workpath", str(ROOT / ".build" / "pyinstaller"),
        "--specpath", str(ROOT / ".build"), str(ROOT / "desktop.py"),
    ], cwd=ROOT, check=True)
    label = "macOS-" + ("AppleSilicon" if os.uname().machine == "arm64" else "Intel") if sys.platform == "darwin" else "Windows-x64"
    archive = OUT / f"LibraryAnalysis-{VERSION}-{label}.zip"
    with tempfile.TemporaryDirectory() as temporary:
        stage = Path(temporary) / f"LibraryAnalysis-{VERSION}"
        stage.mkdir()
        if sys.platform == "darwin":
            app = OUT / "desktop-build" / "LibraryAnalysis.app"
            shutil.copytree(app, stage / app.name, symlinks=True)
        else:
            folder = OUT / "desktop-build" / "LibraryAnalysis"
            shutil.copytree(folder, stage / folder.name)
        shutil.copy2(ROOT / "sample_library_survey.csv", stage)
        shutil.copy2(ROOT / "packaging" / "DESKTOP.md", stage / "START HERE.md")
        if sys.platform == "darwin":
            subprocess.run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(stage), str(archive)], check=True)
        else:
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
                for item in stage.rglob("*"):
                    if item.is_file():
                        bundle.write(item, item.relative_to(stage.parent))
    print(archive)


if __name__ == "__main__":
    build()
