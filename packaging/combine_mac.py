"""Combine native Apple Silicon and Intel builds into one macOS download."""

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile


def combine(arm_archive, intel_archive, output):
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        stage = work / "LibraryAnalysis-0.2.0-alpha"
        stage.mkdir()
        for label, archive in (("Apple Silicon", arm_archive), ("Intel", intel_archive)):
            extracted = work / label.replace(" ", "")
            extracted.mkdir()
            subprocess.run(["ditto", "-x", "-k", str(archive), str(extracted)], check=True)
            source = extracted / stage.name / "LibraryAnalysis.app"
            if not source.exists():
                raise RuntimeError(f"Missing application in {archive}")
            shutil.copytree(source, stage / f"LibraryAnalysis - {label}.app", symlinks=True)
        source_folder = work / "AppleSilicon" / stage.name
        shutil.copy2(source_folder / "sample_library_survey.csv", stage)
        shutil.copy2(source_folder / "START HERE.md", stage)
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", str(stage), str(output)], check=True)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("arm", type=Path)
    parser.add_argument("intel", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    combine(args.arm, args.intel, args.output)
