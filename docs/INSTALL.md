# Library Analysis: Installation and First Run

Version: 0.2.0-alpha.3. Updated September 23, 2026.

## Desktop Download (Recommended)

The compiled desktop packages include Python and the application dependencies. They do not require Python or Ollama to be installed separately. Download the package for your operating system from the [desktop release](https://github.com/keweimao/library-analysis-workflow/releases/tag/v0.2.0-desktop-alpha.3), extract it, and open the application:

- macOS: `LibraryAnalysis-0.2.0-alpha.3-macOS.zip` contains an Apple Silicon app and an Intel app. Open the one matching your Mac.
- Windows x64: `LibraryAnalysis-0.2.0-alpha.3-Windows-x64.zip` contains separate `Install Library Analysis.cmd` and `Start Library Analysis.cmd` launchers.

On Windows, run **Install Library Analysis.cmd** once to download the local runtime and model with progress. Then run **Start Library Analysis.cmd** to check the backend and open the browser. Keep the start window open while using the app. On Mac, select a model and click **Install and open**; keep the desktop window open. Later launches reuse downloads and saved work.

The first download may be several gigabytes. Qwen 9B is intended for a computer with roughly 32 GB RAM; the smaller 4B option is selected by default below 24 GiB and needs more careful result review. A managed computer may still block unsigned applications or downloads. Use the operating system's normal Open/security workflow where permitted; these packages are not signed or notarized.

The included CSV has synthetic sample comments. Saved tasks, imported CSV copies, and downloaded models stay in the user's application-data folder. The first run needs internet; later local analysis can work offline. See [the package's START HERE guide](../packaging/DESKTOP.md) for storage locations and updates.

## Source Launcher (Developer Option)

The source packages are named `LibraryAnalysis-0.2.0-alpha-source-macOS.zip` and `LibraryAnalysis-0.2.0-alpha-source-Windows.zip`. They require a separate Python and Ollama installation. The following instructions apply only to these source packages.

## Requirements

- Python 3.12, 3.13, or 3.14. The launcher checks the version and creates its own environment.
- macOS 14 or newer for current Ollama; Apple Silicon recommended. Intel Macs use CPU inference and will be much slower.
- Windows 10 22H2 or newer, 64-bit x86. Windows ARM has not been qualified.
- 32 GB RAM recommended for the default Qwen 9B model. A smaller model is offered for lower-memory machines; its survey accuracy still needs validation.
- Plan for at least 15-20 GB of free disk space for environment, Ollama, model, and download headroom. Larger models require more.
- Internet during initial Python/Ollama/dependency/model installation. Once installed, local analysis can run offline.

## Install and Open

1. Download the appropriate ZIP and extract the entire folder into a permanent location. On Windows, use **Extract All** before launching.
2. Mac: double-click `Start Library Analysis.command`. Windows: double-click `Start Library Analysis.cmd`.
3. If Python is missing, install Python 3.12-3.14 from python.org and launch again. On Windows include the Python launcher. On macOS, install the python.org certificates if its installer asks.
4. Setup creates a private environment and downloads dependencies. Progress appears in the terminal window.
5. If Ollama is missing, its official download page opens. Install and open Ollama, then return to the terminal and press Enter. This external installer step requires normal OS interaction; the launcher does not bypass device-management restrictions.
6. Choose the initial model: Qwen 9B for the tested balance, Qwen 4B as an unvalidated lower-memory candidate, or Mistral for speed comparison. Model download status and percentages appear in the terminal. Model downloads may take several minutes or longer.
7. Your browser opens the local application automatically. A free localhost port is selected. Keep the terminal window open; Ctrl+C stops the application.

Returning launches reuse the environment and installed model. The optional study preview is disabled in these packages.

If macOS blocks the unsigned launcher, use the OS's Open/Privacy & Security workflow according to institutional policy. Alternatively, open Terminal in the extracted folder and run `python3 launcher.py`. On Windows, `py -3 launcher.py` provides the equivalent. The launchers cannot override institutional application restrictions.

## First Analysis

1. Select New task and the Impact Story template, or start blank and ask a question.
2. Load `sample_library_survey.csv` first. A later CSV replaces the active task data and clears its previous results.
3. Review the topics and labels. Confirm a topic to use only its listed labels; otherwise discovery may propose additional labels. Settings provides the installed model list, batch size, and context budget.
4. Run analysis and inspect progress. Stop retains partial results after the current model call returns. A new run starts over.
5. Click a result label for supporting comments. Review comments allows correction of each topic's labels and immediately recomputes counts. Multiple labels per comment are allowed.
6. Use thumbs and optional notes for usefulness feedback. These do not retrain model weights. Use the export icon to download the analysis and review history, including original comments.

Empty, oversized, or failed comments are marked for review and excluded from label counts until classified or corrected. Counts represent label assignments, not percentages or mutually exclusive totals. Inspect source comments before reporting findings.

## Data and Updates

Packaged launches store files outside the downloaded folder:

- Mac: `~/Library/Application Support/LibraryAnalysis/data/`
- Windows: `%LOCALAPPDATA%\LibraryAnalysis\data\`
- Linux developer use: `~/.local/share/library-analysis/data/`

Uploaded CSVs are copied into that directory. Chats, results, feedback, and model settings are local files. JSON review exports include comment text and should be stored with protected research data. The application does not encrypt those files itself; use the institution's access-controlled account and disk encryption.

To update, stop the old application, extract the new release, and launch it. The same data directory is reused. Back up the data directory before upgrades. Do not run two copies against the same data directory. Repository development data is not automatically imported into a packaged installation.

Removing the extracted folder does not delete saved data or Ollama models. Delete those separately only when intended. Desktop downloads store model weights in the application's user-data folder; source launches use Ollama's configured model storage.

## Troubleshooting

- **No progress during a long analysis:** check Ollama and available RAM. Stop waits for the active request (up to the configured request timeout), then retains partial results.
- **Many unclassified comments:** review context size and number of topics, use an 8K context if memory allows, or shorten the analysis specification. Oversized input is not silently truncated.
- **Setup interrupted:** run the launcher again. Completed dependency/model downloads are reused where supported by pip/Ollama.
- **Cannot download on a managed network:** ask the network administrator about Python package and Ollama download access.
- **Older computer:** use sample data first and measure latency before importing the full dataset. Intel GPU acceleration must be verified on the target system.

## Rebuild and Verification

From the repository, run `python3 packaging/build.py` for source ZIPs. For compiled desktop packages, install `requirements-desktop.txt` on each target operating system and run `python packaging/build_desktop.py`. The automated native-build workflow uses macOS Intel, macOS Apple Silicon, and Windows runners, then combines the two Mac apps into one Mac ZIP. No user data, communications, or development environments are included.

The launcher can be tested in an isolated directory with `python3 launcher.py --home /tmp/library-test --skip-model --no-browser --port 8021`. This skips model preparation only; analysis still requires a local model.

The compiled Mac and Windows apps pass local HTTP smoke tests in native build jobs. Windows first-run setup also passes a runtime download, local service startup, and small-model pull test. Installation and performance on a specific user's computer remain to be checked. See [Windows packaging](WINDOWS_PACKAGING.md) for the two-step design and limitations.

## Future Hosted Deployment

The Python backend can run locally on Linux. Public multi-user hosting is not supported by this alpha: tasks are shared within a single local profile, and the built-in HTTP server binds to loopback. A hosted service requires separate user workspaces, authentication, production serving, TLS, authorization, quota/queue management, and defined retention and export procedures.

Sources checked September 18: [Ollama macOS](https://docs.ollama.com/macos), [Ollama Windows](https://docs.ollama.com/windows), [Ollama FAQ](https://docs.ollama.com/faq).
