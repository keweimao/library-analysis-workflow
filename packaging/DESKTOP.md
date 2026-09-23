# Library Analysis Desktop

This package includes the application and its Python dependencies. You do not need to install Python or Ollama separately.

## Start

- **Mac:** Extract the ZIP and open the app labeled for your Mac (`Apple Silicon` or `Intel`). A single-architecture download contains `LibraryAnalysis.app`.
- **Windows:** Extract the ZIP, run `Install Library Analysis.cmd` once, then run `Start Library Analysis.cmd` whenever you want to use the app. The installation window shows download progress. The start window checks that the local server is working before opening the browser; keep it open while using the app. Press Ctrl+C there to stop.
- **Mac:** Select a local model and choose **Install and open**. Keep the desktop window open while using the app. Later launches reuse downloads and saved tasks; choose **Open analysis** to reopen the browser.

The first download may be several gigabytes. Qwen 9B is intended for computers with about 32 GB RAM or more. The smaller Qwen 4B option uses less memory but needs careful result review. macOS 14+ and Windows 10 22H2+ are supported; Windows x64 and macOS Intel/Apple Silicon builds are separate.

If the operating system blocks an unsigned application, use its normal **Open** or security-settings procedure if allowed by your computer's policy. This package is not code-signed or notarized. The app cannot bypass managed-device restrictions.

The app, model runtime, and downloaded models run on your computer. Internet is required for first-run downloads. No comments are sent to a cloud AI service. Saved tasks and imported CSV copies remain under your user application-data folder:

- Mac: `~/Library/Application Support/LibraryAnalysis/`
- Windows: `%LOCALAPPDATA%\LibraryAnalysis\`

The included CSV contains synthetic test comments. Load it first to check the workflow. A review export includes original comments and should be stored with the same care as the source data.

Close the Mac desktop window or press Ctrl+C in the Windows start window to stop the application. Replacing the extracted app folder does not remove saved tasks or models. Back up the application-data folder before updates.
