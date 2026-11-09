"""Check Gemini's distinct output envelope with fixed synthetic examples."""
import json

import pytest

from run_gemini import parse_response
from resolve_gemini_alias import resolve_record


class TestGeminiResponse:
    """Enforce the same answer rules and prohibit model fallback or tool calls."""

    def test_success_and_abstention(self) -> None:
        """Valid JSON and unreadable answers are retained without rewriting."""
        for card in ['9d', 'unreadable']:
            payload = {'response': json.dumps({'held_card': card}),
                       'stats': {'models': {'gemini-3-flash-preview': {}}, 'tools': {'totalCalls': 0}}}
            result = parse_response(json.dumps(payload), 0, 'gemini-3-flash-preview')
            assert result['status'] == 'completed' and result['held_card'] == card

    def test_strict_answer(self) -> None:
        """Code fences and prose stay invalid, exactly as in the Claude evaluation."""
        for answer in ['```json\n{"held_card":"9d"}\n```', 'Answer: 9d',
                       '{"held_card":"9d","other":1}', '["9d"]']:
            payload = {'response': answer, 'stats': {
                'models': {'gemini-3-flash-preview': {}}, 'tools': {'totalCalls': 0}}}
            result = parse_response(json.dumps(payload), 0, 'gemini-3-flash-preview')
            assert result['status'] == 'invalid_answer' and result['held_card'] is None

    def test_execution_failures(self) -> None:
        """Failed processes, provider errors and malformed envelopes are not valid predictions."""
        for raw, code in [('not JSON', 0), ('[]', 0), ('{"error":{"code":429}}', 1),
                          ('{"response":"{\\"held_card\\":\\"9d\\"}"}', 1)]:
            assert parse_response(raw, code, 'gemini-3-flash-preview')['status'] == 'execution_error'

    def test_model_and_tool_boundaries(self) -> None:
        """Any substituted model or actual tool invocation invalidates the run."""
        for models, calls, expected in [
            ({'gemini-3-flash-preview': {}}, 1, 'unexpected_tool_access'),
            ({'gemini-2.5-flash': {}}, 0, 'model_mismatch'),
            ({'gemini-3-flash-preview': {}, 'other': {}}, 0, 'model_mismatch'),
        ]:
            payload = {'response': '{"held_card":"9d"}',
                       'stats': {'models': models, 'tools': {'totalCalls': calls}}}
            assert parse_response(json.dumps(payload), 0, 'gemini-3-flash-preview')['status'] == expected


class TestDocumentedAlias:
    """Preserve requested IDs and reject substitutions beyond the known retired alias."""

    def test_explicit_stable_identity(self) -> None:
        """The actual model gets its own name while original validation stays auditable."""
        original = {'model': 'gemini-3.1-flash-lite-preview', 'returncode': 0,
                    'status': 'model_mismatch', 'resolved_models': ['gemini-3.1-flash-lite']}
        raw = json.dumps({'response': '{"held_card":"9d"}', 'stats': {
            'models': {'gemini-3.1-flash-lite': {}}, 'tools': {'totalCalls': 0}}})
        result = resolve_record(original, raw)
        assert result['model'] == 'gemini-3.1-flash-lite'
        assert result['requested_model'] == 'gemini-3.1-flash-lite-preview'
        assert result['status'] == 'completed' and result['held_card'] == '9d'
        assert original['status'] == result['original_validation_status'] == 'model_mismatch'

    def test_other_substitutions_rejected(self) -> None:
        """Retirement handling must not accept arbitrary fallback models."""
        original = {'model': 'gemini-3.1-flash-lite-preview', 'returncode': 0,
                    'status': 'model_mismatch', 'resolved_models': ['gemini-2.5-flash']}
        with pytest.raises(ValueError):
            resolve_record(original, '{}')
