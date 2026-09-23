import json
import os
import tempfile
import threading
import unittest
from contextlib import ExitStack
from pathlib import Path
import urllib.request
import urllib.error
from unittest.mock import patch, Mock

import app


class AlphaTests(unittest.TestCase):
    def test_pipeline_fingerprint_in_source_and_frozen_layout(self):
        source_digest = app.pipeline_sha256()
        self.assertEqual(len(source_digest), 64)
        with tempfile.TemporaryDirectory() as folder:
            digest_path = Path(folder) / "pipeline.sha256"
            digest_path.write_text(source_digest + "\n", encoding="ascii")
            with patch.object(app, "__file__", str(Path(folder) / "missing-app.py")), patch.object(app, "PIPELINE_DIGEST_PATH", digest_path):
                self.assertEqual(app.pipeline_sha256(), source_digest)
                digest_path.write_text("invalid", encoding="ascii")
                with self.assertRaisesRegex(RuntimeError, "fingerprint"):
                    app.pipeline_sha256()

    def test_local_boundary(self):
        for name in ("qwen3.5:cloud", "foo-cloud", "../../bad model"):
            with self.assertRaises(ValueError):
                app.validate_model_name(name)
        with patch.dict(os.environ, {"OLLAMA_BASE_URL": "https://example.com"}):
            with self.assertRaises(ValueError):
                app.LocalModel()

    def test_cloud_alias_cannot_masquerade_as_installed_local_model(self):
        model = app.LocalModel()
        tags, metadata = Mock(), Mock()
        tags.json.return_value = {"models": [{"name": "local-looking:latest"}]}
        metadata.json.return_value = {"capabilities": ["completion"], "remote_host": "https://example.org"}
        with patch.object(app.requests, "get", return_value=tags), patch.object(app.requests, "post", return_value=metadata):
            self.assertFalse(model.is_model_installed("local-looking:latest"))

    def test_live_job_survives_snapshot_reload(self):
        state = app.ProjectState()
        state.analysis_job = app.AnalysisJob(job_id="live", running=True)
        with patch.dict(app.RUN_EVENTS, {"live": threading.Event()}):
            restored = app.store._state_from_payload(app.asdict(state))
        self.assertTrue(restored.analysis_job.running)
        interrupted = app.store._state_from_payload(app.asdict(state))
        self.assertEqual(interrupted.analysis_job.stage, "interrupted")

    def test_context_limit_prevents_silent_truncation(self):
        model = app.LocalModel()
        with patch.object(app.requests, "post") as request:
            result = model._generate_json({"text": "z" * 10000}, {"type": "object"}, 300)
        self.assertIsNone(result)
        request.assert_not_called()
        self.assertIn("context budget", model.last_error)

    def test_schema_is_enforced_after_generation(self):
        model = app.LocalModel()
        response = Mock()
        response.json.return_value = {"response": '{"wrong": 3}'}
        with patch.object(app.requests, "post", return_value=response):
            self.assertIsNone(model._generate_json({}, {"type": "object", "required": ["answer"]}, 300))

    def test_impact_template_fits_one_row_at_4k(self):
        model = app.LocalModel()
        model.context_length = 4096
        variables = app.create_template_state("impact_story").variables
        for variable in variables:
            if variable.name == "keyword":
                variable.labels = ['databases', 'search strategies', 'journals', 'access', 'links', 'study rooms', 'quiet area', 'instruction sessions', 'course reserves', 'printing', 'computers', 'payment process', 'friendly staff', 'knowledgeable staff', 'time saved']
            variable.clarity = "ready"
        response = Mock()
        response.json.return_value = {"response": json.dumps({"results": [{"row_id": 0, "variables": {v.name: [] for v in variables}, "quote_worthy": False, "rationale": "No supported label"}]})}
        with patch.object(app.requests, "post", return_value=response) as call:
            result = model.analyze_comments([{"row_id": 0, "text": "The research librarian helped me find databases for my senior design project, and that support saved me a lot of time.", "context": {"department": "Engineering", "respondent_type": "undergraduate"}}], variables)
        self.assertIsNotNone(result)
        call.assert_called_once()

    def test_long_batches_split_and_preserve_successful_rows(self):
        model = app.LocalModel()
        variable = app.VariableSpec("area", "Area", ["staff"], clarity="ready")
        output = {"results": [{"row_id": 0, "variables": {"area": ["staff"]}}]}
        with patch.object(model, "_generate_json", side_effect=[None, output, None]):
            result = model.analyze_comments([{"row_id": 0}, {"row_id": 1}], [variable])
        self.assertEqual([r["row_id"] for r in result], [0])

    def test_duplicates_do_not_inflate_counts(self):
        state = app.ProjectState(row_results=[{"analysis": {"area": ["staff", "staff"]}}])
        self.assertEqual(app.aggregate_results(state)["area"]["counts"]["staff"], 1)

    def test_study_events_disabled_for_personal_use(self):
        with patch.object(app, "STUDY_MODE", False), patch.object(app, "STUDY_EVENTS_PATH") as path:
            app.study_store.append_event("", "test", {})
        path.open.assert_not_called()

    def test_task_path_rejected(self):
        for operation in (app.store.switch_task, app.store.delete_task, app.store._load_task):
            with self.assertRaises(ValueError):
                operation("../settings")


class ReviewAPITests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        directory = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        for name, path in {"DATA_DIR": directory, "TASK_DIR": directory / "tasks", "UPLOAD_DIR": directory / "uploads", "STATE_PATH": directory / "state.json", "CURRENT_TASK_PATH": directory / "current.txt"}.items():
            self.stack.enter_context(patch.object(app, name, path))
        self.stack.enter_context(patch.object(app, "STUDY_MODE", False))
        self.stack.enter_context(patch.object(app.model, "available", return_value=False))
        store = app.Store()
        self.stack.enter_context(patch.object(app, "store", store))
        store.state.variables = [app.VariableSpec("area", "Area", ["staff", "facilities"], clarity="ready")]
        store.state.row_results = [{"row_index": 0, "text": "Helpful staff", "analysis": {"area": ["staff"]}, "method": "model"}]
        store.state.analysis_job = app.AnalysisJob(job_id="test-run", complete=True, processed=1, total=1)
        store.state.aggregate_results = app.aggregate_results(store.state)
        store.save()
        self.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close_server)
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, path, payload=None, headers=None):
        request = urllib.request.Request(self.base + path, data=json.dumps(payload).encode() if payload is not None else None, headers={"Content-Type": "application/json", **(headers or {})})
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def test_feedback_toggle_correction_and_export(self):
        for expected in ("up", None):
            result = self.request("/api/feedback", {"variable": "area", "label": "staff", "rating": "up"})
            self.assertEqual(result["feedback_events"][-1]["rating"], expected)
        self.request("/api/feedback", {"variable": "area", "label": "staff", "comment": "Please review this"})
        corrected = self.request("/api/correction", {"row_index": 0, "variable": "area", "labels": ["facilities"]})
        self.assertEqual(corrected["aggregate_results"]["area"]["counts"], {"facilities": 1})
        exported = self.request("/api/review.json")
        self.assertEqual(exported["row_results"][0]["original_analysis"]["area"], ["staff"])
        self.assertEqual(len(exported["feedback_events"]), 4)
        self.assertTrue(all(event["job_id"] == "test-run" for event in exported["feedback_events"]))

    def test_cross_origin_and_stale_task_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request("/api/feedback", {}, {"Origin": "https://example.org"})
        self.assertEqual(caught.exception.code, 403)
        caught.exception.close()
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request("/api/feedback", {}, {"X-Task-ID": "wrong"})
        self.assertEqual(caught.exception.code, 409)
        caught.exception.close()

    def test_stale_results_and_invalid_json_rejected(self):
        app.store.state.results_stale = True
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request("/api/correction", {"row_index": 0, "variable": "area", "labels": ["staff"]})
        caught.exception.close()
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request("/api/tasks", ["invalid"])
        caught.exception.close()

    def test_cancel_sets_live_event(self):
        event = threading.Event()
        with patch.dict(app.RUN_EVENTS, {"test-run": event}):
            self.request("/api/cancel", {})
        self.assertTrue(event.is_set())

    def test_confirm_labels_and_edit_marks_old_results_stale(self):
        result = self.request("/api/variables", {"action": "approve_labels", "name": "area"})
        self.assertEqual(result["variables"][0]["clarity"], "ready")
        self.assertTrue(result["results_stale"])

    def test_single_choice_correction_rejects_conflicting_values(self):
        app.store.state.variables = [app.VariableSpec("sentiment", "Tone", ["positive", "negative"], clarity="ready")]
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request("/api/correction", {"row_index": 0, "variable": "sentiment", "labels": ["positive", "negative"]})
        self.assertEqual(caught.exception.code, 400)
        caught.exception.close()


if __name__ == "__main__":
    unittest.main()
