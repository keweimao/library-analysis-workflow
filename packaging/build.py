"""Build source distributions from an explicit allowlist, excluding research data."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.2.0-alpha"
FILES = ["app.py", "launcher.py", "requirements-lock.txt", "requirements.txt", "sample_library_survey.csv",
         "static/app.js", "static/index.html", "static/styles.css", "docs/INSTALL.md", "docs/architecture.md"]


def build():
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    for platform, launcher in [("macOS", "Start Library Analysis.command"), ("Windows", "Start Library Analysis.cmd")]:
        archive = output / f"LibraryAnalysis-{VERSION}-{platform}.zip"
        prefix = f"LibraryAnalysis-{VERSION}/"
        manifest = {}
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for relative in FILES:
                data = (ROOT / relative).read_bytes()
                bundle.writestr(prefix + relative, data)
                manifest[relative] = hashlib.sha256(data).hexdigest()
            readme = (ROOT / "packaging/READ ME.txt").read_bytes()
            bundle.writestr(prefix + "READ ME.txt", readme)
            manifest["READ ME.txt"] = hashlib.sha256(readme).hexdigest()
            data = (ROOT / "packaging" / launcher).read_bytes()
            info = zipfile.ZipInfo(prefix + launcher)
            info.create_system = 3
            info.external_attr = 0o100755 << 16
            bundle.writestr(info, data)
            manifest[launcher] = hashlib.sha256(data).hexdigest()
            bundle.writestr(prefix + "MANIFEST.json", json.dumps({"version": VERSION, "sha256": manifest}, indent=2))
        print(f"{archive.name}: {hashlib.sha256(archive.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    build()
