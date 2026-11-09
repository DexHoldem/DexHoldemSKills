"""Verify input isolation and strict extraction without contacting a model."""
import base64
import json
import tempfile
from pathlib import Path

import pytest

from run_claude import build_message, parse_response


class TestInputIsolation:
    """Ensure only the selected image bytes and neutral prompt reach inference."""

    def test_exact_message_and_private_exclusion(self) -> None:
        """Private answers and source paths cannot enter the serialized payload."""
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            (root / 'inputs').mkdir()
            (root / 'inputs/image.jpg').write_bytes(b'exact-image-bytes')
            (root / 'private.json').write_text('{"answer":"Ad"}')
            sample = {'id': 'hc001', 'image': 'inputs/image.jpg', 'prompt': 'Read the held card.'}
            payload = build_message(root, sample)
            content = json.loads(payload)['message']['content']
            assert content == [
                {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg',
                                           'data': base64.b64encode(b'exact-image-bytes').decode()}},
                {'type': 'text', 'text': 'Read the held card.'},
            ]
            assert work not in payload and 'Ad' not in payload and 'hc001' not in payload
            with pytest.raises(ValueError):
                build_message(root, {**sample, 'image': 'private.json'})
            with pytest.raises(ValueError):
                build_message(root, {**sample, 'label': 'Ad'})


class TestResponseExtraction:
    """Reject prose, tool-enabled runs, substituted models and infrastructure errors."""

    def test_strict_extraction(self) -> None:
        """Only a successful exact JSON response becomes a prediction."""
        init = {'type': 'system', 'subtype': 'init', 'tools': [], 'mcp_servers': []}
        for answer, expected in [('{"held_card":"Kh"}', 'completed'),
                                 ('The answer is {"held_card":"Kh"}', 'invalid_answer'),
                                 ('```json\n{"held_card":"Kh"}\n```', 'invalid_answer'),
                                 ('{"held_card":"Kh","extra":1}', 'invalid_answer')]:
            event = {'type': 'result', 'subtype': 'success', 'is_error': False,
                     'modelUsage': {'claude-opus-5-5': {}}, 'result': answer}
            raw = json.dumps(init)+'\n'+json.dumps(event)
            result = parse_response(raw, 0, 'claude-opus-5-5')
            assert result['status'] == expected
            assert result['held_card'] == ('Kh' if expected == 'completed' else None)

    def test_failure_and_model_boundaries(self) -> None:
        """Model mismatch, enabled tools and CLI failure cannot silently count as success."""
        for tools, models, code, expected in [
            ([], {'claude-opus-5-5': {}}, 1, 'execution_error'),
            (['Read'], {'claude-opus-5-5': {}}, 0, 'unexpected_tool_access'),
            ([], {'claude-sonnet-5': {}}, 0, 'model_mismatch'),
            ([], {'claude-opus-5-5': {}}, 0, 'completed'),
        ]:
            events = [{'type': 'system', 'subtype': 'init', 'tools': tools, 'mcp_servers': []},
                      {'type': 'result', 'subtype': 'success', 'is_error': False,
                       'modelUsage': models, 'result': '{"held_card":"unreadable"}'}]
            result = parse_response('\n'.join(json.dumps(e) for e in events), code, 'claude-opus-5-5')
            assert result['status'] == expected
