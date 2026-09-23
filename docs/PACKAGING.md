# Desktop Packaging

## Approach

Use native, self-contained desktop bundles for local single-user installs. PyInstaller includes Python, the application, and its Python dependencies. A small Qt setup window downloads a pinned Ollama runtime and a selected local model into the user's application-data directory. Later launches reuse them. Docker is not used for this desktop release because users would still need to install and start Docker Desktop and configure its virtualization backend.

The Mac download contains separate Apple Silicon and Intel apps; the Windows download contains an x64 executable. The app serves its existing browser interface on a random localhost port and starts its own Ollama process on a separate localhost port. Closing the desktop window stops both. The app uses its own model directory and disables Ollama cloud access for the process it starts.

## First Run

1. Extract the full ZIP and open the executable for the computer.
2. Select Qwen 9B, Qwen 4B, or Mistral, then click **Install and open**. Below 16 GB RAM, the smaller model is preselected.
3. The window checks for a current local Ollama binary. If needed, it downloads the pinned official standalone archive with byte progress and SHA-256 verification, then unpacks it in the user profile.
4. The window starts Ollama on localhost and streams model-pull progress from its API.
5. The application opens in the default browser. Tasks, settings, model files, and the runtime remain in the user profile between launches.

The runtime archive is pinned in `desktop.py`, including its version and checksum. Update both values together after testing a newer Ollama release. Model weights are obtained through Ollama's registry; the download can be several gigabytes. Setup cancellation leaves saved tasks intact.

## Build and Verify

Install `requirements-desktop.txt` on each target OS and run `python packaging/build_desktop.py`. Native binaries cannot be built reliably for another operating system from one machine. The GitHub Actions workflow builds Windows x64, Intel Mac, and Apple Silicon Mac independently, runs each frozen binary's local HTTP smoke test, and combines the two Mac apps into one ZIP. It produces two distribution packages: Mac and Windows.

For source-only packages, `python packaging/build.py` builds separate ZIPs with the `source-` name. Source packages still require a Python installation and are not the recommended end-user download. All package builds use explicit file lists or app resources; no real datasets or internal records are included.

The bundles are currently unsigned. macOS may require the user to open the app through its security settings, and Windows SmartScreen or a managed-device policy may prompt or block it. Removing those prompts requires platform-specific signing, and macOS distribution at scale also requires notarization. Native Windows installation and performance on the target computer remain an acceptance test even after CI smoke checks pass.

## Storage and Updates

- Mac: `~/Library/Application Support/LibraryAnalysis/`
- Windows: `%LOCALAPPDATA%\LibraryAnalysis\`

Updates replace the extracted application folder; saved work and downloaded models remain in the user profile. Back up that profile before a major upgrade. The desktop package itself does not install system-wide software or require a container runtime.
