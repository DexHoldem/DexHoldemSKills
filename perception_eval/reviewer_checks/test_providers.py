"""Provider identity, isolation, and transport-retry policy checks."""
import base64
import json
import tempfile
from pathlib import Path

from multi_campaign import service_failure
from providers import claude_message, parse_provider


class TestProviderParsing:
    """Require exact model identity, no tools, and a strict final JSON object."""

    def test_claude_identity_and_prediction(self) -> None:
        """A tool-free response from the requested model is accepted."""
        events = [{'type': 'system', 'subtype': 'init', 'tools': [], 'mcp_servers': []},
                  {'type': 'result', 'subtype': 'success', 'is_error': False,
                   'modelUsage': {'claude-opus-5-5': {}}, 'result': '{"loop_stage":"idle"}'}]
        stdout = '\n'.join(json.dumps(e) for e in events)
        result = parse_provider(stdout, 0, 'claude-opus-5-5', 'claude')
        assert result['status'] == 'completed'
        assert result['prediction'] == {'loop_stage': 'idle'}
        assert parse_provider(stdout, 0, 'claude-sonnet-5', 'claude')['status'] == 'model_mismatch'

    def test_claude_tools_rejected(self) -> None:
        """A valid-looking final answer cannot override the tool-isolation gate."""
        events = [{'type': 'system', 'subtype': 'init', 'tools': ['Read'], 'mcp_servers': []},
                  {'type': 'result', 'subtype': 'success', 'is_error': False,
                   'modelUsage': {'claude-opus-5-5': {}}, 'result': '{}'}]
        assert parse_provider('\n'.join(json.dumps(e) for e in events), 0,
                              'claude-opus-5-5', 'claude')['status'] == 'unexpected_tool_access'

    def test_gemini_alias_must_be_declared(self) -> None:
        """An explicit recorded alias is accepted; silent model substitution is not."""
        stdout = json.dumps({'response': '{"table":{"scene_stable":true}}',
                             'stats': {'models': {'gemini-3.1-flash-lite': {}}, 'tools': {'totalCalls': 0}}})
        assert parse_provider(stdout, 0, 'gemini-3.1-flash-lite-preview', 'gemini')['status'] == 'model_mismatch'
        result = parse_provider(stdout, 0, 'gemini-3.1-flash-lite-preview', 'gemini', 'gemini-3.1-flash-lite')
        assert result['status'] == 'completed'
        assert result['resolved_models'] == ['gemini-3.1-flash-lite']

    def test_fences_remain_format_errors(self) -> None:
        """All providers follow the same strict JSON contract."""
        stdout = json.dumps({'response': '```json\n{}\n```',
                             'stats': {'models': {'gemini-3-flash-preview': {}}, 'tools': {'totalCalls': 0}}})
        assert parse_provider(stdout, 0, 'gemini-3-flash-preview', 'gemini')['status'] == 'invalid_json'

    def test_image_bytes_and_order_preserved(self) -> None:
        """Image transport preserves every supplied file and its chronological order."""
        with tempfile.TemporaryDirectory() as work:
            paths = [Path(work)/'a.jpg', Path(work)/'b.jpg']
            for path, data in zip(paths, (b'first', b'second')):
                path.write_bytes(data)
            blocks = json.loads(claude_message(paths, 'task'))['message']['content']
            assert [base64.b64decode(b['source']['data']) for b in blocks[:-1]] == [b'first', b'second']
            assert blocks[-1] == {'type': 'text', 'text': 'task'}


class TestServiceFailures:
    """Never decide whether to retry based on semantic answer correctness."""

    def test_no_answer_quota_and_transport(self) -> None:
        """Only error evidence is classified; a response makes the trial ineligible."""
        with tempfile.TemporaryDirectory() as work:
            path = Path(work)
            (path/'stderr.txt').write_text('')
            (path/'stdout.jsonl').write_text('You have hit your usage limit')
            assert service_failure({'status': 'execution_error'}, path) == 'quota'
            (path/'stdout.jsonl').write_text('HTTP 503 overloaded')
            assert service_failure({'status': 'execution_error'}, path) == 'transient_service'
            assert service_failure({'status': 'invalid_json'}, path) is None
            assert service_failure({'status': 'execution_error', 'assistant_messages': ['{}']}, path) is None
