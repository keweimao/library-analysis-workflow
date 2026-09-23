"""Visible, two-step Windows setup and local server launcher."""

import argparse
import json
import os
from pathlib import Path
import sys
import threading
import urllib.request
import webbrowser

from desktop import MODELS, SetupWorker, api, ram_gb, self_test
from launcher import home_directory, lock_home


class ConsoleSetup(SetupWorker):
    def report(self, message, percent=-1):
        suffix = f" ({percent}%)" if percent >= 0 else ""
        print(message + suffix, flush=True)


def read_settings(profile):
    path = profile / "data" / "settings.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def selected_model(profile, requested=None):
    existing = read_settings(profile).get("model")
    if requested:
        return requested
    if existing:
        return existing
    models = [item[0] for item in MODELS]
    default = 1 if (ram_gb() or 32) < 24 else 0
    print("Choose a local model:")
    for index, (_, label) in enumerate(MODELS, start=1):
        print(f"  {index}. {label}")
    choice = input(f"Selection [{default + 1}]: ").strip()
    if not choice:
        return models[default]
    if choice not in {str(i) for i in range(1, len(models) + 1)}:
        raise ValueError("Choose a number from the list.")
    return models[int(choice) - 1]


def save_settings(profile, model):
    folder = profile / "data"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "settings.json"
    values = read_settings(profile)
    values["model"] = model
    values.setdefault("batch_size", 3)
    values.setdefault("context_length", 4096)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(values, indent=2), encoding="utf-8")
    temporary.replace(path)


def install(profile, model):
    print("[1/3] Preparing the local model runtime", flush=True)
    worker = ConsoleSetup(profile, model)
    binary = worker.prepare_binary()
    print("[2/3] Starting the local model service", flush=True)
    base, process = worker.start_ollama(binary)
    try:
        print(f"[3/3] Preparing {model}", flush=True)
        worker.prepare_model(base)
        save_settings(profile, model)
    finally:
        if process.poll() is None:
            process.terminate()
    print("Installation complete. Use Start Library Analysis.cmd to open the app.", flush=True)


def check_url(url):
    for path in ("/api/health", "/api/state", "/"):
        with urllib.request.urlopen(url + path, timeout=15) as response:
            if response.status != 200:
                raise RuntimeError(f"The local server returned HTTP {response.status} for {path}.")
            response.read()


def start(profile, no_browser=False, smoke=False):
    settings = read_settings(profile)
    model = settings.get("model")
    if not model and not smoke:
        raise RuntimeError("No model is configured. Run Install Library Analysis.cmd first.")
    process = None
    server = None
    thread = None
    try:
        if not smoke:
            worker = ConsoleSetup(profile, model)
            binary = worker.prepare_binary()
            print("Starting the local model service...", flush=True)
            base, process = worker.start_ollama(binary)
        else:
            base = "http://127.0.0.1:1"
        os.environ.update({
            "LIBRARY_DATA_DIR": str(profile / "data"),
            "OLLAMA_BASE_URL": base,
            "OLLAMA_NO_CLOUD": "1",
            "LIBRARY_STUDY_MODE": "0",
            "LIBRARY_OPEN_BROWSER": "0",
        })
        import app
        from http.server import ThreadingHTTPServer

        server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        server.daemon_threads = True
        server.block_on_close = False
        url = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        check_url(url)
        print(f"Library Analysis is ready at {url}", flush=True)
        if smoke:
            return
        if not no_browser:
            webbrowser.open(url)
        print("Keep this window open. Press Ctrl+C to stop.", flush=True)
        while thread.is_alive():
            thread.join(timeout=0.5)
        raise RuntimeError("The local web server stopped unexpectedly.")
    finally:
        if server:
            server.shutdown()
            server.server_close()
        if thread:
            thread.join(timeout=5)
        if process and process.poll() is None:
            process.terminate()


def main():
    parser = argparse.ArgumentParser(description="Library Analysis Windows desktop launcher")
    parser.add_argument("command", choices=("install", "start"))
    parser.add_argument("--model", help="Model to install; otherwise use the saved model or prompt")
    parser.add_argument("--home", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--smoke", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    profile = args.home or home_directory()
    profile.mkdir(parents=True, exist_ok=True)
    handle = lock_home(profile)
    try:
        if args.command == "install":
            model = selected_model(profile, args.model)
            if "cloud" in model.lower():
                raise ValueError("Only local models are supported.")
            install(profile, model)
        else:
            start(profile, args.no_browser, args.smoke)
    finally:
        handle.close()


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        os._exit(self_test())
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped.")
    except Exception as exc:
        print(f"Library Analysis could not continue: {exc}", file=sys.stderr, flush=True)
        print(f"Check {home_directory() / 'ollama.log'} if the model service failed.", file=sys.stderr)
        sys.exit(1)
