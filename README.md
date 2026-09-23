# Local Survey Analysis Workflow

This is a local prototype for interactive analysis of open-ended survey comments.

The workflow uses a local small language model: conversational planning and label discovery define the analysis, bounded batches classify individual comments, and code aggregates validated records into source-linked findings. See the [architecture overview](docs/architecture.md).

The app supports:

- CSV upload and comment-column selection.
- Chat-guided task clarification.
- Tracked variables, labels, and clarity status.
- Per-comment map analysis into structured fields.
- Reduce-stage aggregation into counts and representative comments.
- Local Ollama inference with schema validation and explicit unclassified-row review.
- Local task history and feedback logging.

## Run

Download the [Mac or Windows desktop package](https://github.com/keweimao/library-analysis-workflow/releases/tag/v0.2.0-desktop-alpha.2) and follow [installation and first run](docs/INSTALL.md). The compiled downloads include Python and application dependencies. Windows uses separate install and start scripts; Mac uses a setup window. Both download a local Ollama runtime and model with progress. See [desktop packaging](docs/PACKAGING.md) for the build and first-run design.

```bash
cd library-analysis-workflow
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
PYTHONPYCACHEPREFIX="$PWD/.pycache" .venv/bin/python app.py
```

Then open:

```text
http://127.0.0.1:8000
```

## Local Model

If Ollama is running locally, the app will call:

```text
http://127.0.0.1:11434/api/generate
```

The recommended default model is `qwen3.5:9b`, selected for its structured-output quality and local latency on the included sample. Override it with:

```bash
OLLAMA_MODEL=mistral PYTHONPYCACHEPREFIX="$PWD/.pycache" .venv/bin/python app.py
```

Without Ollama, the interface remains available but analysis reports that the selected model is unavailable. Model failures never silently substitute keyword rules. Unclassified comments are retained for review.

## Workflow

1. Upload a CSV. Uploading another CSV replaces the task's active dataset and clears results tied to the previous data.
2. Confirm or change the text/comment column.
3. Ask the analytic question in chat.
4. Review tracked concepts and labels.
5. Run analysis.
6. Review aggregates and open any label to verify its source comments.
7. Rate aggregate labels as useful or needing correction.
8. Review comments, save corrected classifications, and export the analysis with its feedback and model provenance.

Blank tasks start with no predefined concepts. The app combines conversational model planning with a small library-oriented recognition catalog, then discovers provisional labels from the loaded data before mapping comments in schema-constrained batches.

See [the architecture overview](docs/architecture.md) for the computational workflow. The optional study-preview code is disabled in packaged launches and is not a ready-to-use consent workflow. Keep actual survey data and user records outside the repository.
