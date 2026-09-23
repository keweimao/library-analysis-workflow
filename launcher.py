"""User-level desktop bootstrap; only the Python standard library is required."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
import venv
import webbrowser

ROOT = Path(__file__).resolve().parent


def home_directory():
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "LibraryAnalysis"
    if sys.platform == "win32":
        return Path(os.getenv("LOCALAPPDATA", str(Path.home()))) / "LibraryAnalysis"
    return Path(os.getenv("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "library-analysis"


def lock_home(home):
    handle = (home / "launcher.lock").open("a+b")
    handle.write(b"0")
    handle.flush()
    handle.seek(0)
    try:
        if sys.platform == "win32":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        raise RuntimeError("Library Analysis is already running for this profile. Use its existing window or stop it first.")
    return handle


def ollama_api(path="tags", payload=None, timeout=5):
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Content-Type": "application/json"},
    )
    return urllib.request.urlopen(request, timeout=timeout)


def ready():
    try:
        with ollama_api() as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def find_ollama():
    candidates = [shutil.which("ollama")]
    if sys.platform == "darwin":
        candidates += ["/Applications/Ollama.app/Contents/Resources/ollama", str(Path.home() / "Applications/Ollama.app/Contents/Resources/ollama")]
    elif sys.platform == "win32":
        candidates += [str(Path(os.getenv("LOCALAPPDATA", "")) / "Programs/Ollama/ollama.exe")]
    return next((str(path) for path in candidates if path and Path(path).is_file()), None)


def prepare_ollama(home):
    if ready():
        print("[3/5] Ollama is running locally.", flush=True)
        return
    binary = find_ollama()
    if not binary:
        url = "https://ollama.com/download/" + ("windows" if sys.platform == "win32" else "mac" if sys.platform == "darwin" else "linux")
        print("[3/5] Install Ollama from its official installer, then return here.", flush=True)
        print(url, flush=True)
        webbrowser.open(url)
        input("Install and open Ollama. Press Enter when ready: ")
        binary = find_ollama()
    if not ready() and binary:
        with (home / "ollama-launch.log").open("a", encoding="utf-8") as log:
            environment = {**os.environ, "OLLAMA_HOST": "127.0.0.1:11434", "OLLAMA_NO_CLOUD": "1"}
            subprocess.Popen([binary, "serve"], env=environment, stdout=log, stderr=log)
        for _ in range(30):
            if ready():
                return
            print("Waiting for local Ollama...", flush=True)
            time.sleep(1)
    if not ready():
        raise RuntimeError("Ollama is not ready. Open Ollama and run this launcher again.")


def pull_model(name):
    print(f"[4/5] Preparing {name}. Downloads can take several minutes.", flush=True)
    with ollama_api() as response:
        models = json.load(response).get("models", [])
    if any(item.get("name") in {name, name + ":latest"} for item in models):
        print("Model already installed.", flush=True)
        return
    with ollama_api("pull", {"model": name, "stream": True}, timeout=600) as response:
        last = None
        for line in response:
            item = json.loads(line)
            if item.get("error"):
                raise RuntimeError(item["error"])
            total = item.get("total", 0)
            percent = int(item.get("completed", 0) * 100 / total) if total else None
            marker = (item.get("status"), percent)
            if marker != last:
                print(item.get("status", "Downloading") + (f" {percent}%" if percent is not None else ""), flush=True)
                last = marker


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--home", type=Path, default=home_directory())
    parser.add_argument("--model", default=None)
    parser.add_argument("--skip-model", action="store_true", help="Launch the UI without preparing Ollama (testing only)")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    if sys.version_info < (3, 12) or sys.version_info >= (3, 15):
        raise RuntimeError("Python 3.12, 3.13, or 3.14 is required. Install it from python.org, then retry.")
    home = args.home.expanduser().resolve()
    home.mkdir(parents=True, exist_ok=True)
    profile_lock = lock_home(home)
    print("Library Analysis alpha setup", flush=True)
    print(f"Your data and environment: {home}", flush=True)
    environment_dir = home / ("python-" + platform.python_version())
    interpreter = environment_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    print("[1/5] Checking the private Python environment...", flush=True)
    if not interpreter.exists():
        venv.EnvBuilder(with_pip=True).create(environment_dir)
    requirements = ROOT / "requirements-lock.txt"
    if not requirements.exists():
        requirements = ROOT / "requirements.txt"
    digest = hashlib.sha256(requirements.read_bytes()).hexdigest()
    marker = environment_dir / "requirements.sha256"
    print("[2/5] Checking application dependencies...", flush=True)
    if not marker.exists() or marker.read_text() != digest:
        subprocess.run([str(interpreter), "-m", "pip", "install", "--only-binary=:all:", "-r", str(requirements)], check=True)
        marker.write_text(digest)
    (home / "data").mkdir(exist_ok=True)
    settings_path = home / "data/settings.json"
    settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
    selected = args.model or settings.get("model")
    if not args.skip_model:
        prepare_ollama(home)
        if not selected:
            print("Model: 1 = Qwen 9B (recommended for 32 GB), 2 = Qwen 4B (smaller, needs validation), 3 = Mistral (fast comparison)")
            choice = input("Choose 1, 2, or 3 [1]: ").strip()
            selected = {"": "qwen3.5:9b", "1": "qwen3.5:9b", "2": "qwen3.5:4b", "3": "mistral:latest"}.get(choice)
            if not selected:
                raise RuntimeError("Please run again and choose 1, 2, or 3.")
        if "cloud" in selected.lower():
            raise RuntimeError("Only local models are supported.")
        pull_model(selected)
        settings.update({"model": selected})
        settings.setdefault("batch_size", 3)
        settings.setdefault("context_length", 4096)
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    print("[5/5] Opening Library Analysis. Keep this window open; Ctrl+C stops the app.", flush=True)
    environment = {**os.environ, "LIBRARY_DATA_DIR": str(home / "data"), "PORT": str(args.port),
                   "LIBRARY_OPEN_BROWSER": "0" if args.no_browser else "1", "LIBRARY_STUDY_MODE": "0",
                   "OLLAMA_BASE_URL": "http://127.0.0.1:11434", "PYTHONUTF8": "1"}
    subprocess.run([str(interpreter), str(ROOT / "app.py")], cwd=str(ROOT), env=environment, check=True)
    profile_lock.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped.")
    except Exception as exc:
        print(f"Setup could not finish: {exc}\nYour saved data is retained. Resolve the issue and run the launcher again.", flush=True)
        sys.exit(1)
