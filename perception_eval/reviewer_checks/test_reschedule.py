"""Check that cache-friendly scheduling cannot overwrite an existing answer."""
import json
import tempfile
from pathlib import Path

import pytest

from reschedule import RESERVED, matches_scheduler, publish


class TestReservationPublication:
    """Validate atomic promotion and refusal to replace real inference results."""

    def test_publishes_raw_evidence_before_final_record(self) -> None:
        """A reserved slot receives the exact staged record and raw response."""
        with tempfile.TemporaryDirectory() as work:
            source, target = Path(work)/'stage', Path(work)/'canonical'
            source.mkdir(); target.mkdir()
            (target/'record.json').write_text(json.dumps({'status': RESERVED}))
            text = json.dumps({'status': 'completed', 'prediction': {'loop_stage': 'idle'}})
            (source/'record.json').write_text(text)
            (source/'stdout.jsonl').write_text('RAW RESPONSE\n')
            (source/'stderr.txt').write_text('')
            publish(source, target)
            assert (target/'record.json').read_text() == text
            assert (target/'stdout.jsonl').read_text() == 'RAW RESPONSE\n'
            assert not (target/'record.json.publishing').exists()

    def test_cannot_overwrite_completed_or_failed_answers(self) -> None:
        """An existing actual attempt, including failure, is never replaced."""
        with tempfile.TemporaryDirectory() as work:
            source, target = Path(work)/'stage', Path(work)/'canonical'
            source.mkdir(); target.mkdir()
            (source/'record.json').write_text(json.dumps({'status': 'completed'}))
            for status in ('completed', 'invalid_json', 'execution_error'):
                original = json.dumps({'status': status})
                (target/'record.json').write_text(original)
                with pytest.raises(ValueError, match='Refusing to overwrite'):
                    publish(source, target)
                assert (target/'record.json').read_text() == original

    def test_only_exact_python_scheduler_matches(self) -> None:
        """Wrappers and unrelated Python jobs cannot be suspended accidentally."""
        script = Path(__file__).with_name('multi_campaign.py').resolve()
        root = Path('/private/tmp/owned-campaign')
        command = f'/usr/bin/python3 {script} --output {root} --family claude --workers 8'
        assert matches_scheduler(command, root)
        assert not matches_scheduler('uv run '+command, root)
        assert not matches_scheduler('/bin/zsh -lc '+command, root)
        assert not matches_scheduler(command.replace(str(root), '/private/tmp/other'), root)
        assert not matches_scheduler(command.replace('multi_campaign.py', 'unrelated.py'), root)
