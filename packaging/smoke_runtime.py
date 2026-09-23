"""Exercise the desktop first-run Ollama setup on a native runner."""

import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import desktop


def main():
    profile = Path(tempfile.mkdtemp(prefix="library-runtime-check-"))
    process = None
    try:
        worker = desktop.SetupWorker(profile, "qwen3.5:0.8b")
        last = [-10]

        def report(message, percent):
            if percent < 0 or percent >= last[0] + 10:
                print(message, f"{percent}%" if percent >= 0 else "", flush=True)
                if percent >= 0:
                    last[0] = percent

        worker.update.connect(report)
        desktop.find_system_ollama = lambda: None
        binary = worker.prepare_binary()
        base, process = worker.start_ollama(binary)
        with desktop.api(base, "tags") as response:
            assert isinstance(json.load(response)["models"], list)
        worker.prepare_model(base)
        print("Runtime and model pull passed", flush=True)
    finally:
        if process and process.poll() is None:
            process.terminate()
            process.wait(timeout=20)
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
