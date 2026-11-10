"""Check quota-only recovery without making provider requests."""
import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from resume_claude import DEFERRED, ZONE, pending, quota_only, reset_time


class TestClaudeQuotaResume:
    """Completed or malformed model answers must remain untouched."""

    def test_requires_zero_usage_and_no_model_answer(self) -> None:
        """Quota wording alone cannot authorize replacing an answer."""
        raw = {'status':'execution_error','result':"You've hit your 5-hour limit",
               'prediction':None,'resolved_models':[], 'usage':{'input_tokens':0,'output_tokens':0}}
        assert quota_only(raw)
        assert not quota_only({**raw, 'status':'invalid_json'})
        assert not quota_only({**raw, 'resolved_models':['claude-opus-5-5']})
        assert not quota_only({**raw, 'usage':{'input_tokens':0,'output_tokens':1}})

    def test_resolves_next_reset_with_margin(self) -> None:
        """Midnight rollover and PM timestamps preserve Singapore timezone."""
        message = "You've hit your 5-hour limit · resets 2:50am (Asia/Singapore)"
        assert reset_time(message, datetime(2026,11,10,22,0,tzinfo=ZONE)) == datetime(2026,11,11,2,51,tzinfo=ZONE)
        assert reset_time(message, datetime(2026,11,11,1,0,tzinfo=ZONE)) == datetime(2026,11,11,2,51,tzinfo=ZONE)
        assert reset_time('resets 12:05pm (Asia/Singapore)', datetime(2026,11,11,1,tzinfo=ZONE)).hour == 12
        with pytest.raises(ValueError):
            reset_time('resets next week', datetime.now(ZONE))

    def test_selects_only_deferred_claude(self) -> None:
        """Other providers and existing completed/invalid records are excluded."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cases = [('claude-opus-5-5','p1',DEFERRED), ('claude-opus-5-5','p2','invalid_json'),
                     ('claude-opus-5-5','p3','completed'), ('gpt-6-sol','p1',DEFERRED)]
            for model, problem, status in cases:
                path = root/'models'/model/'trials/annotated/repeat_1'/problem/'record.json'
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps({'status':status}))
            assert [p.parent.name for p in pending(root)] == ['p1']
