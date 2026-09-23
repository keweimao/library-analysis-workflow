# Windows Packaging Decision

The Windows distribution is a console-visible, two-step native bundle. `Install Library Analysis.cmd` prepares a local Ollama runtime and model; `Start Library Analysis.cmd` starts the model and web server, checks the health, state, and page endpoints, and only then opens the browser. Startup failures remain visible in the console. The included `LibraryAnalysis.exe` bundles Python and application dependencies, so no Python installation or virtual environment is needed.

This is preferable to Docker Desktop for one person on one computer: Docker adds a separate runtime, virtualization requirements, and managed-device approvals. It is also preferable to an automatic Python installer script, which would change the user's Python installation and still need to manage pip. The official Python embeddable distribution does not support normal pip dependency management. The app uses Ollama's standalone Windows CLI archive in the user's application-data folder. The runtime archive is pinned and checksum-verified before extraction; model downloads show streamed progress. No administrator privileges are intended, although managed-device security policies may block unsigned software or downloads.

## Package contents

- `Install Library Analysis.cmd`: one-time setup, repeatable to change/retry the model.
- `Start Library Analysis.cmd`: regular launch, health check, and visible diagnostics.
- `LibraryAnalysis/`: one-folder, console-mode PyInstaller app and bundled Python dependencies.
- `START HERE.md` and a synthetic sample CSV.

Data, model files, and runtime are under `%LOCALAPPDATA%\LibraryAnalysis`, outside the extracted package. The app and Ollama bind to loopback only; the browser uses a dynamically selected local port. The first run needs internet and free disk space for the runtime archive and model. Later launches reuse both. `ollama.log` in the application-data folder records local model-service startup errors.

## Verification and limits

The build runs on a native Windows x64 CI runner. It checks that the frozen executable serves `/api/health`, `/api/state`, and `/`, and that the startup command exits cleanly after a test run. A separate Windows test downloads the standalone Ollama archive, starts it, and pulls a small model. These tests do not measure latency on every user's hardware. The package is unsigned; Windows SmartScreen or institutional policy may require approval. The app is single-user and local-only, not a public web-server deployment.
