"""Check that paid-route recovery cannot select an answered trial."""
import json
import tempfile
from pathlib import Path

from recover_gemini_google import MODEL, eligible


class TestRecoverySelection:
    """Validate quota-only selection against real, isolated files."""

    def test_quota_without_answer_is_eligible(self) -> None:
        """Select an explicit 429 with no saved summary."""
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run = root / "run"
            run.mkdir()
            (run / "gemini_stderr.txt").write_text("429 RESOURCE_EXHAUSTED")
            record = root / "records" / MODEL / "repeat_3" / "p26" / "record.json"
            record.parent.mkdir(parents=True)
            record.write_text(json.dumps({"status": "gemini_failed", "run_dir": str(run)}))
            assert eligible(root, "p26")
            (run / "visual_summary.json").write_text("malformed answer")
            assert not eligible(root, "p26")

    def test_unstarted_and_nonquota_failure(self) -> None:
        """Accept only pristine missing trials; reject other infrastructure errors."""
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            assert eligible(root, "p32")
            run = root / "run"
            run.mkdir()
            (run / "gemini_stderr.txt").write_text("403 forbidden")
            record = root / "records" / MODEL / "repeat_3" / "p32" / "record.json"
            record.parent.mkdir(parents=True)
            record.write_text(json.dumps({"status": "gemini_failed", "run_dir": str(run)}))
            assert not eligible(root, "p32")

    def test_invalid_output_never_selected(self) -> None:
        """Do not retry invalid output even if stderr also mentions quota."""
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run = root / "run"
            run.mkdir()
            (run / "gemini_stderr.txt").write_text("429 RESOURCE_EXHAUSTED")
            record = root / "records" / MODEL / "repeat_3" / "p26" / "record.json"
            record.parent.mkdir(parents=True)
            record.write_text(json.dumps({"status": "invalid_outputs", "run_dir": str(run)}))
            assert not eligible(root, "p26")
