import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

import app


class WorkflowTests(unittest.TestCase):
    def test_study_consent_and_responses_use_pseudonymous_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            participant_dir = root / "participants"
            events_path = root / "events.jsonl"
            with (
                patch.object(app, "STUDY_MODE", True),
                patch.object(app, "PARTICIPANT_DIR", participant_dir),
                patch.object(app, "STUDY_EVENTS_PATH", events_path),
            ):
                study = app.StudyStore()
                participant_id = "a" * 32
                record = study.consent(
                    participant_id,
                    {
                        "accepted": True,
                        "age_confirmed": True,
                        "responses": {"role": "Assessment Librarian"},
                    },
                )
                self.assertTrue(study.public_status(participant_id)["consented"])
                self.assertEqual(record["responses"]["role"]["value"], "Assessment Librarian")
                self.assertNotIn("email", record)
                self.assertTrue(events_path.exists())

    def test_study_consent_requires_adult_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(app, "PARTICIPANT_DIR", root / "participants"),
                patch.object(app, "STUDY_EVENTS_PATH", root / "events.jsonl"),
            ):
                study = app.StudyStore()
                with self.assertRaisesRegex(ValueError, "at least 18"):
                    study.consent("b" * 32, {"accepted": True, "age_confirmed": False})

    def test_run_command_requires_explicit_command(self):
        self.assertTrue(app.is_run_command("Run analysis."))
        self.assertTrue(app.is_run_command("start analysis now"))
        self.assertFalse(app.is_run_command("Help me analyze areas of excellence"))

    def test_targeted_labels_are_assigned_to_named_concept(self):
        found = app.targeted_labels_from_message("Areas include staff, facilities, technology, and others.")
        self.assertEqual(found["area"], ["staff", "facilities", "technology", "others"])

    def test_model_output_is_normalized_and_fixed_labels_are_enforced(self):
        variables = [
            app.VariableSpec(
                name="sentiment",
                description="Tone",
                labels=["positive", "negative", "mixed", "neutral"],
                clarity="ready",
            )
        ]
        result = app.normalize_model_analysis(
            {"variables": {"sentiment": ["Positive", "invented"]}, "quote_worthy": True, "rationale": "clear praise"},
            variables,
        )
        self.assertEqual(result["sentiment"], ["positive"])
        self.assertEqual(result["quote_worthy"], "yes")

    def test_aggregates_retain_source_row_references(self):
        state = app.ProjectState(
            row_results=[
                {"row_index": 4, "text": "Helpful staff.", "analysis": {"area": ["staff"], "rationale": "direct praise"}}
            ]
        )
        result = app.aggregate_results(state)
        self.assertEqual(result["area"]["counts"]["staff"], 1)
        self.assertEqual(result["area"]["sample_quotes"]["staff"][0]["row_index"], 4)

    def test_background_publish_does_not_replace_active_task(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dir = root / "data"
            task_dir = data_dir / "tasks"
            upload_dir = data_dir / "uploads"
            task_dir.mkdir(parents=True)
            upload_dir.mkdir()
            with (
                patch.object(app, "DATA_DIR", data_dir),
                patch.object(app, "TASK_DIR", task_dir),
                patch.object(app, "UPLOAD_DIR", upload_dir),
                patch.object(app, "STATE_PATH", data_dir / "project_state.json"),
                patch.object(app, "CURRENT_TASK_PATH", data_dir / "current_task.txt"),
            ):
                store = app.Store()
                first = store.load_task_snapshot(store.state.task_id)
                second = store.new_task()
                first.analysis_job.message = "Finished in background"
                store.publish_task(first)
                self.assertEqual(store.state.task_id, second.task_id)
                self.assertEqual(store._load_task(first.task_id).analysis_job.message, "Finished in background")

    def test_replacing_data_keeps_one_source_and_clears_stale_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dir = root / "data"
            task_dir = data_dir / "tasks"
            upload_dir = data_dir / "uploads"
            task_dir.mkdir(parents=True)
            upload_dir.mkdir()
            with (
                patch.object(app, "DATA_DIR", data_dir),
                patch.object(app, "TASK_DIR", task_dir),
                patch.object(app, "UPLOAD_DIR", upload_dir),
                patch.object(app, "STATE_PATH", data_dir / "project_state.json"),
                patch.object(app, "CURRENT_TASK_PATH", data_dir / "current_task.txt"),
            ):
                store = app.Store()
                old = app.DataSource("aaaaaaaaaaaa", "old.csv", 2, ["comment"], "comment")
                new = app.DataSource("bbbbbbbbbbbb", "new.csv", 3, ["text"], "text")
                (upload_dir / "aaaaaaaaaaaa.csv").write_text("comment\nold\n")
                store.state.data_sources = [old]
                store.state.row_results = [{"row_index": 0}]
                store.state.aggregate_results = {"area": {"counts": {"staff": 1}}}
                store.state.feedback = [{"variable": "area", "label": "staff", "rating": "up"}]
                store.save()

                previous = store.replace_data_source(new)
                store.delete_unreferenced_uploads([item.id for item in previous])

                self.assertEqual([source.filename for source in store.state.data_sources], ["new.csv"])
                self.assertEqual(store.state.row_results, [])
                self.assertEqual(store.state.aggregate_results, {})
                self.assertEqual(store.state.feedback, [])
                self.assertFalse((upload_dir / "aaaaaaaaaaaa.csv").exists())

    def test_existing_multi_upload_tasks_migrate_to_latest_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dir = root / "data"
            task_dir = data_dir / "tasks"
            upload_dir = data_dir / "uploads"
            task_dir.mkdir(parents=True)
            upload_dir.mkdir()
            payload = app.ProjectState(task_id="cccccccccccc")
            payload.data_sources = [
                app.DataSource("aaaaaaaaaaaa", "old.csv", 1, ["comment"], "comment"),
                app.DataSource("bbbbbbbbbbbb", "latest.csv", 2, ["comment"], "comment"),
            ]
            (task_dir / "cccccccccccc.json").write_text(json.dumps(app.asdict(payload)))
            (upload_dir / "aaaaaaaaaaaa.csv").write_text("comment\nold\n")
            (upload_dir / "bbbbbbbbbbbb.csv").write_text("comment\nlatest\n")
            with (
                patch.object(app, "DATA_DIR", data_dir),
                patch.object(app, "TASK_DIR", task_dir),
                patch.object(app, "UPLOAD_DIR", upload_dir),
                patch.object(app, "STATE_PATH", data_dir / "project_state.json"),
                patch.object(app, "CURRENT_TASK_PATH", data_dir / "current_task.txt"),
            ):
                store = app.Store()
                self.assertEqual([source.filename for source in store.state.data_sources], ["latest.csv"])
                self.assertFalse((upload_dir / "aaaaaaaaaaaa.csv").exists())
                self.assertTrue((upload_dir / "bbbbbbbbbbbb.csv").exists())


if __name__ == "__main__":
    unittest.main()
