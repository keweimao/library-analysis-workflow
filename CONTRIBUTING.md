# Public Repository Policy

This repository is for application code, tests, packaging/build files, synthetic sample data, and general user/developer documentation only.

Do not add real survey responses, participant information, task exports, meeting notes, correspondence, approval or agreement documents, consent/recruitment drafts, institution-specific IT responses, local paths, credentials, or screenshots containing internal information. Keep sensitive data outside Git. A `.gitignore` entry does not protect a file that is already tracked or added explicitly.

Before opening a pull request or publishing a release:

1. Run `python3 scripts/check_public_tree.py`.
2. Inspect `git status --short` and the full diff, including new documentation and sample files. Confirm examples are synthetic and contain no identifying details.
3. Inspect release ZIP contents. Publish only reviewed binaries and general instructions.

The checker intentionally allows only reviewed file paths and flags common private-content patterns. Additions to its allowlist need explicit review; passing the checker is not proof that a document is safe to publish.
