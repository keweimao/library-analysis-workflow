"""Self-contained desktop setup and launcher for the local analysis application."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import threading
import urllib.error
import urllib.request
import traceback
import zipfile

from PySide6.QtCore import QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QComboBox, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPlainTextEdit, QProgressBar, QPushButton,
    QVBoxLayout, QWidget,
)

from launcher import home_directory, lock_home


OLLAMA_VERSION = "v0.34.3"
OLLAMA_ASSETS = {
    "darwin": (
        "ollama-darwin.tgz",
        "2c45865f94bce0d4d1d2567603dd2fdacaf375585220a175aa4800105193d36e",
    ),
    "win32": (
        "ollama-windows-amd64.zip",
        "306ce9e81e3491d147f558e60d7a389499f244d10f71859c6e4e899241d1b4ae",
    ),
}
MODELS = (
    ("qwen3.5:9b", "Qwen 9B - recommended with 32 GB RAM"),
    ("qwen3.5:4b", "Qwen 4B - lighter; review results carefully"),
    ("mistral:latest", "Mistral - smaller comparison model"),
)


def ram_gb():
    if sys.platform == "darwin":
        try:
            return int(subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()) / 2**30
        except (OSError, ValueError, subprocess.CalledProcessError):
            return None
    if sys.platform == "win32":
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                        ("total_phys", ctypes.c_ulonglong), ("avail_phys", ctypes.c_ulonglong),
                        ("total_page", ctypes.c_ulonglong), ("avail_page", ctypes.c_ulonglong),
                        ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong),
                        ("avail_extended", ctypes.c_ulonglong)]

        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return status.total_phys / 2**30
    return None


def free_local_port():
    with socket.socket() as candidate:
        candidate.bind(("127.0.0.1", 0))
        return candidate.getsockname()[1]


def api(base, path, payload=None, timeout=30):
    request = urllib.request.Request(
        base + "/api/" + path,
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers={"Content-Type": "application/json"},
    )
    return urllib.request.urlopen(request, timeout=timeout)


def safe_member(name):
    path = Path(name.replace("\\", "/"))
    return bool(path.parts) and not path.is_absolute() and ".." not in path.parts and ":" not in path.parts[0]


class SetupCancelled(Exception):
    pass


def find_system_ollama():
    candidates = [shutil.which("ollama")]
    if sys.platform == "darwin":
        candidates += ["/Applications/Ollama.app/Contents/Resources/ollama",
                       str(Path.home() / "Applications/Ollama.app/Contents/Resources/ollama")]
    else:
        candidates += [str(Path(os.getenv("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe")]
    return next((str(value) for value in candidates if value and Path(value).is_file()), None)


class SetupWorker(QThread):
    update = Signal(str, int)
    finished_setup = Signal(str, object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, profile, model):
        super().__init__()
        self.profile = profile
        self.model = model

    def report(self, message, percent=-1):
        self.update.emit(message, percent)

    def download(self, url, destination, digest):
        temporary = destination.with_suffix(destination.suffix + ".part")
        request = urllib.request.Request(url, headers={"User-Agent": "LibraryAnalysis/0.2"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response, temporary.open("wb") as output:
                total = int(response.headers.get("Content-Length", "0"))
                completed = 0
                checksum = hashlib.sha256()
                last = -1
                while True:
                    if self.isInterruptionRequested():
                        raise SetupCancelled()
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    output.write(block)
                    checksum.update(block)
                    completed += len(block)
                    percent = int(completed * 100 / total) if total else -1
                    if percent != last:
                        self.report("Downloading local model runtime", percent)
                        last = percent
            if checksum.hexdigest() != digest:
                raise RuntimeError("The runtime download did not match its checksum. Please retry.")
            temporary.replace(destination)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

    def prepare_binary(self):
        system = find_system_ollama()
        if system:
            try:
                version = subprocess.check_output([system, "--version"], text=True, timeout=10)
                current = tuple(int(value) for value in version.split("ollama version is ")[-1].strip().split(".")[:3])
                required = tuple(int(value) for value in OLLAMA_VERSION.lstrip("v").split("."))
                if current >= required:
                    self.report("Using an installed Ollama runtime", 100)
                    return system
            except (OSError, ValueError, subprocess.SubprocessError):
                pass
        runtime = self.profile / "runtime" / OLLAMA_VERSION
        binary = runtime / ("ollama.exe" if sys.platform == "win32" else "ollama")
        if binary.is_file():
            self.report("Local model runtime is ready", 100)
            return str(binary)
        asset, digest = OLLAMA_ASSETS[sys.platform]
        url = f"https://github.com/ollama/ollama/releases/download/{OLLAMA_VERSION}/{asset}"
        runtime.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime.parent) as work:
            folder = Path(work)
            archive = folder / asset
            self.report("Downloading local model runtime", 0)
            self.download(url, archive, digest)
            self.report("Unpacking local model runtime")
            extracted = folder / "extracted"
            extracted.mkdir()
            if sys.platform == "win32":
                with zipfile.ZipFile(archive) as bundle:
                    if not all(safe_member(item.filename) for item in bundle.infolist()):
                        raise RuntimeError("The runtime archive contains an unsafe path.")
                    bundle.extractall(extracted)
            else:
                with tarfile.open(archive, "r:gz") as bundle:
                    if not all(safe_member(item.name) for item in bundle.getmembers()):
                        raise RuntimeError("The runtime archive contains an unsafe path.")
                    bundle.extractall(extracted, filter="data")
            if self.isInterruptionRequested():
                raise SetupCancelled()
            candidates = list(extracted.rglob(binary.name))
            if not candidates:
                raise RuntimeError("The runtime archive did not contain Ollama.")
            root = candidates[0].parent
            shutil.move(str(root), str(runtime))
        binary.chmod(binary.stat().st_mode | 0o111)
        self.report("Local model runtime is ready", 100)
        return str(binary)

    def start_ollama(self, binary):
        port = free_local_port()
        base = f"http://127.0.0.1:{port}"
        models = self.profile / "models"
        models.mkdir(parents=True, exist_ok=True)
        environment = {**os.environ, "OLLAMA_HOST": f"127.0.0.1:{port}",
                       "OLLAMA_MODELS": str(models), "OLLAMA_NO_CLOUD": "1"}
        log_path = self.profile / "ollama.log"
        log = log_path.open("a", encoding="utf-8")
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        process = subprocess.Popen([binary, "serve"], env=environment, stdout=log,
                                   stderr=subprocess.STDOUT, creationflags=flags)
        log.close()
        for _ in range(90):
            if self.isInterruptionRequested():
                process.terminate()
                raise SetupCancelled()
            if process.poll() is not None:
                raise RuntimeError(f"The local model runtime exited. See {log_path}")
            try:
                with api(base, "tags", timeout=2):
                    return base, process
            except (OSError, urllib.error.URLError):
                self.msleep(500)
        process.terminate()
        raise RuntimeError(f"The local model runtime did not start. See {log_path}")

    def prepare_model(self, base):
        with api(base, "tags") as response:
            installed = json.load(response).get("models", [])
        if any(item.get("name") in {self.model, self.model + ":latest"} for item in installed):
            self.report("Selected model is already installed", 100)
            return
        self.report(f"Downloading {self.model}", 0)
        with api(base, "pull", {"model": self.model, "stream": True}, timeout=900) as response:
            last = None
            for line in response:
                if self.isInterruptionRequested():
                    raise SetupCancelled()
                item = json.loads(line)
                if item.get("error"):
                    raise RuntimeError(item["error"])
                total = item.get("total", 0)
                percent = int(item.get("completed", 0) * 100 / total) if total else -1
                marker = (item.get("status"), percent)
                if marker != last:
                    self.report(item.get("status", "Preparing model"), percent)
                    last = marker
        self.report(f"{self.model} is ready", 100)

    def run(self):
        process = None
        try:
            binary = self.prepare_binary()
            self.report("Starting the local model service")
            base, process = self.start_ollama(binary)
            self.prepare_model(base)
            self.finished_setup.emit(base, process)
        except SetupCancelled:
            if process and process.poll() is None:
                process.terminate()
            self.cancelled.emit()
        except Exception as exc:
            if process and process.poll() is None:
                process.terminate()
            self.failed.emit(str(exc))


class DesktopWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.profile = home_directory()
        self.profile.mkdir(parents=True, exist_ok=True)
        self.profile_lock = lock_home(self.profile)
        self.model_process = None
        self.server = None
        self.worker = None
        self.close_when_done = False
        self.url = ""
        self.setWindowTitle("Library Analysis")
        self.resize(560, 390)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)
        title = QLabel("Library Analysis")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addWidget(QLabel("Analyze text with a model running on this computer."))
        self.model_label = QLabel("Local model")
        layout.addWidget(self.model_label)
        self.choice = QComboBox()
        for name, label in MODELS:
            self.choice.addItem(label, name)
        memory = ram_gb()
        if memory is not None and memory < 16:
            self.choice.setCurrentIndex(1)
            layout.addWidget(QLabel("This computer has limited memory. The smaller model is selected."))
        layout.addWidget(self.choice)
        self.status = QLabel("Ready to set up")
        layout.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Setup progress will appear here.")
        layout.addWidget(self.log, 1)
        buttons = QHBoxLayout()
        self.start_button = QPushButton("Install and open")
        self.start_button.clicked.connect(self.begin)
        self.open_button = QPushButton("Open analysis")
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self.open_browser)
        self.cancel_button = QPushButton("Cancel setup")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_setup)
        buttons.addWidget(self.start_button)
        buttons.addWidget(self.open_button)
        buttons.addWidget(self.cancel_button)
        buttons.addStretch()
        layout.addLayout(buttons)
        self.setCentralWidget(container)
        self.setStyleSheet("""
            QWidget { font-size: 13px; color: #263135; background: #f6f8f8; }
            QLabel#title { font-size: 24px; font-weight: 700; color: #15343a; }
            QComboBox, QPlainTextEdit { background: white; border: 1px solid #b9c7c9; border-radius: 5px; padding: 6px; }
            QPushButton { background: #17635c; color: white; border: none; border-radius: 5px; padding: 9px 15px; }
            QPushButton:disabled { background: #bdc8c8; color: #4b5657; }
            QProgressBar { border: 1px solid #b9c7c9; border-radius: 4px; background: white; text-align: center; height: 20px; }
            QProgressBar::chunk { background: #2c937f; }
        """)

    def begin(self):
        if self.worker and self.worker.isRunning():
            return
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.choice.setEnabled(False)
        self.log.clear()
        self.worker = SetupWorker(self.profile, self.choice.currentData())
        self.worker.update.connect(self.on_update)
        self.worker.failed.connect(self.on_error)
        self.worker.cancelled.connect(self.on_cancelled)
        self.worker.finished_setup.connect(self.on_ready)
        self.worker.start()

    def on_update(self, message, percent):
        self.status.setText(message)
        self.log.appendPlainText(message + (f" ({percent}%)" if percent >= 0 else ""))
        if percent < 0:
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 100)
            self.progress.setValue(percent)

    def on_error(self, message):
        if self.close_when_done:
            return
        if self.model_process and self.model_process.poll() is None:
            self.model_process.terminate()
            self.model_process = None
        self.on_update("Setup needs attention", -1)
        self.log.appendPlainText(message)
        self.start_button.setEnabled(True)
        self.choice.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QMessageBox.warning(self, "Setup could not finish", message + "\n\nYour saved data is unchanged. Try again after resolving the issue.")

    def cancel_setup(self):
        if self.worker and self.worker.isRunning():
            self.worker.requestInterruption()
            self.cancel_button.setEnabled(False)
            self.on_update("Stopping setup", -1)

    def on_cancelled(self):
        self.on_update("Setup stopped", 0)
        self.start_button.setEnabled(True)
        self.choice.setEnabled(True)
        self.cancel_button.setEnabled(False)
        if self.close_when_done:
            return

    def on_ready(self, base, process):
        self.model_process = process
        if self.close_when_done:
            process.terminate()
            self.model_process = None
            return
        try:
            self.on_update("Starting Library Analysis", -1)
            data = self.profile / "data"
            data.mkdir(exist_ok=True)
            settings = data / "settings.json"
            values = json.loads(settings.read_text()) if settings.exists() else {}
            values["model"] = self.choice.currentData()
            values.setdefault("batch_size", 3)
            values.setdefault("context_length", 4096)
            temporary = settings.with_suffix(".tmp")
            temporary.write_text(json.dumps(values, indent=2), encoding="utf-8")
            temporary.replace(settings)
            os.environ.update({"LIBRARY_DATA_DIR": str(data), "OLLAMA_BASE_URL": base,
                               "LIBRARY_STUDY_MODE": "0", "LIBRARY_OPEN_BROWSER": "0"})
            import app
            from http.server import ThreadingHTTPServer
            import threading

            self.server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
            self.server.daemon_threads = True
            self.url = f"http://127.0.0.1:{self.server.server_port}"
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
            self.on_update("Ready", 100)
            self.cancel_button.setEnabled(False)
            self.start_button.setText("Running")
            self.open_button.setEnabled(True)
            self.open_browser()
        except Exception as exc:
            self.on_error(str(exc))

    def open_browser(self):
        if self.url:
            QDesktopServices.openUrl(QUrl(self.url))

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            if not self.close_when_done:
                self.close_when_done = True
                self.worker.finished.connect(self.close)
            self.cancel_setup()
            event.ignore()
            return
        if self.server:
            import app
            for item in list(app.RUN_EVENTS.values()):
                item.set()
            self.server.shutdown()
            self.server.server_close()
        if self.model_process and self.model_process.poll() is None:
            self.model_process.terminate()
        self.profile_lock.close()
        event.accept()


def self_test():
    folder = Path(tempfile.mkdtemp(prefix="library-desktop-smoke-"))
    os.environ["LIBRARY_DATA_DIR"] = str(folder)
    os.environ["LIBRARY_STUDY_MODE"] = "0"
    import app
    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
    server.daemon_threads = True
    server.block_on_close = False
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    with urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/api/health", timeout=10) as response:
        assert json.load(response)["app"] == "library-analysis"
    with urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/", timeout=10) as response:
        assert b"Interactive Language Models" in response.read()
    # The smoke process exits immediately; Windows can keep imported database files open.
    return 0


def main():
    if sys.platform not in OLLAMA_ASSETS:
        raise RuntimeError("This desktop build supports macOS and Windows only.")
    application = QApplication(sys.argv)
    try:
        window = DesktopWindow()
    except RuntimeError as exc:
        QMessageBox.warning(None, "Already running", str(exc))
        return 1
    window.show()
    return application.exec()


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        try:
            outcome = self_test()
        except Exception:
            traceback.print_exc()
            outcome = 1
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(outcome)
    sys.exit(main())
