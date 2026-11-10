"""Check annotated-input preservation using real temporary files."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from native_ablation import digest
from supplement_annotated_gpt import prepare


class TestAnnotatedSupplement:
    """Verify exact preservation and refusal of changed original inputs."""

    def test_preserves_annotations_caches_and_current_link(self) -> None:
        """The annotated arm must restore every original input without labels."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            repo, baseline, target = root / "repo", root / "baseline", root / "output"
            problem = repo / "bench/problems/p1"
            (problem / "s0").mkdir(parents=True)
            (problem / "s0/00_capture.jpg").write_bytes(b"image")
            (problem / "s0/01_parsed_state.md").write_text("annotated state")
            (problem / "action_sequence.json").write_text('{"stage": "acting"}')
            (problem / "s_current").symlink_to("s0")
            (repo / "bench/problems/ground_truth.json").write_text("offline gold")
            source = baseline / "paper_gpt_source/runner.py"
            source.parent.mkdir(parents=True)
            source.write_text("archived source")
            manifest = {"problems": {"p1": {
                "retained": {"s0/00_capture.jpg": {"sha256": digest(problem / "s0/00_capture.jpg")},
                             "s_current": {"symlink": "s0"}},
                "removed": {name: digest(problem / name) for name in ("s0/01_parsed_state.md", "action_sequence.json")}}}}
            (baseline / "protocol.json").write_text(json.dumps(manifest))
            (baseline / "gpt_paper_provenance.json").write_text(json.dumps({"snapshot_sha256": {"runner.py": digest(source)}}))
            result = prepare(repo, baseline, target)
            assert result["retains_annotated_history"] is True
            assert (target / "problems/p1/s_current").readlink() == Path("s0")
            assert (target / "problems/p1/s0/01_parsed_state.md").read_bytes() == (problem / "s0/01_parsed_state.md").read_bytes()
            assert (target / "problems/p1/action_sequence.json").read_bytes() == (problem / "action_sequence.json").read_bytes()
            assert not (target / "problems/ground_truth.json").exists()
            assert prepare(repo, baseline, target) == result
            (problem / "s0/01_parsed_state.md").write_text("changed")
            with pytest.raises(ValueError, match="Original input changed"):
                prepare(repo, baseline, target)
