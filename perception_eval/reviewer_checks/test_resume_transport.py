"""Verify that transport recovery preserves answers and quota-deferred work."""
import json
import tempfile
from pathlib import Path

from reschedule import RESERVED
from resume_transport import recover


class TestTransportRecovery:
    """Only a no-answer network error can create a new reserved trial."""

    def test_only_no_answer_transport_failure_is_retried(self) -> None:
        """Incorrect/invalid answers and Claude quota slots remain untouched."""
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            (root/'rescheduling.json').write_text(json.dumps({'reserved_tasks': []}))
            cases = [('gpt-6-sol','p1','execution_error'), ('gpt-6-sol','p2','invalid_json'),
                     ('gpt-6-sol','p3','completed'), ('claude-opus-5-5','p1','deferred_until_claude_quota_reset')]
            for model, pid, status in cases:
                case = root/'models'/model/'trials/annotated/repeat_1'/pid
                case.mkdir(parents=True)
                record = {'status':status,'model':model,'problem':pid,'condition':'annotated','repeat':1}
                (case/'record.json').write_text(json.dumps(record))
                (case/'stdout.jsonl').write_text('')
                (case/'stderr.txt').write_text('Runner timeout; no answer selected.')
            report = recover(root)
            assert len(report['recovered_no_answer_trials']) == 1
            case = root/'models/gpt-6-sol/trials/annotated/repeat_1/p1'
            assert json.loads((case/'record.json').read_text())['status'] == RESERVED
            backup = root/'models/gpt-6-sol/attempts/annotated/repeat_1/p1/before_lower_concurrency/record.json'
            assert json.loads(backup.read_text())['status'] == 'execution_error'
            for model, pid, status in cases[1:]:
                assert json.loads((root/'models'/model/'trials/annotated/repeat_1'/pid/'record.json').read_text())['status'] == status
