"""Check Codex output validation and isolation without network/model calls."""
import json
from pathlib import Path

from run_codex import build_command, parse_response


def stream(answer: str, extra: list[dict] | None = None) -> str:
    """Return a synthetic JSONL turn for answer (str) and optional events (list[dict])."""
    events = [{'type': 'thread.started', 'thread_id': 'example'},
              {'type': 'turn.started'}, *(extra or []),
              {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': answer}},
              {'type': 'turn.completed', 'usage': {'input_tokens': 100, 'output_tokens': 10}}]
    return '\n'.join(json.dumps(event) for event in events)


class TestCodexResponse:
    """Reject tool use, incomplete turns, protocol changes and malformed answers."""

    def test_success_and_abstention(self) -> None:
        """Retain valid answers and explicitly avoid claiming backend model attestation."""
        for card in ['9d', 'unreadable']:
            result = parse_response(stream(json.dumps({'held_card': card})), 0, 'gpt-6-sol')
            assert result['status'] == 'completed' and result['held_card'] == card
            assert result['resolved_models'] == [] and result['requested_model'] == 'gpt-6-sol'
        commentary = {'type': 'item.completed', 'item': {
            'type': 'agent_message', 'text': 'I will inspect the held card.'}}
        result = parse_response(stream('{"held_card":"9d"}', [commentary]), 0, 'gpt-6-sol')
        assert result['status'] == 'completed' and len(result['assistant_messages']) == 2
        # Do not search earlier messages if the final response is malformed.
        earlier = {'type': 'item.completed', 'item': {
            'type': 'agent_message', 'text': '{"held_card":"9d"}'}}
        assert parse_response(stream('Answer: 9d', [earlier]), 0, 'gpt-6-sol')['status'] == 'invalid_answer'

    def test_strict_answer(self) -> None:
        """Code fences, prose, extra keys and non-objects remain invalid."""
        for answer in ['```json\n{"held_card":"9d"}\n```', 'Answer: 9d',
                       '{"held_card":"9d","other":1}', '["9d"]']:
            result = parse_response(stream(answer), 0, 'gpt-6-sol')
            assert result['status'] == 'invalid_answer' and result['held_card'] is None

    def test_failed_and_incomplete_turns(self) -> None:
        """No completed output can override an API error or a process failure."""
        valid = stream('{"held_card":"9d"}')
        for raw, code in [('bad JSON', 0), ('[]', 0), (valid, 1),
                          ('\n'.join(valid.splitlines()[:-1]), 0),
                          (valid+'\n'+json.dumps({'type': 'error', 'message': 'failed'}), 0)]:
            assert parse_response(raw, code, 'gpt-6-sol')['status'] == 'execution_error'

    def test_tools_and_configuration_changes(self) -> None:
        """Reject even started tool calls and CLI warnings about fallback or dropped tier."""
        for event, expected in [
            ({'type': 'item.started', 'item': {'type': 'command_execution'}}, 'unexpected_tool_access'),
            ({'type': 'item.completed', 'item': {'type': 'mcp_tool_call'}}, 'unexpected_tool_access'),
            ({'type': 'item.completed', 'item': {'type': 'error', 'message': 'Using fallback metadata'}},
             'configuration_mismatch'),
            ({'type': 'item.completed', 'item': {'type': 'error', 'message': 'Tier will be omitted'}},
             'configuration_mismatch'),
        ]:
            assert parse_response(stream('{"held_card":"9d"}', [event]), 0, 'gpt-6-sol')['status'] == expected


class TestCodexInput:
    """Check the actual command builder's context and tool restrictions."""

    def test_image_only_isolation(self) -> None:
        """Attach a neutral image path, disable tools and omit private dataset information."""
        command = build_command('gpt-6-sol', Path('/tmp/isolated'))
        assert command[-3:] == ['-i', '/tmp/isolated/image.jpg', '-']
        assert command[command.index('-m')+1] == 'gpt-6-sol'
        for token in ['--ignore-user-config', '--ignore-rules', '--ephemeral',
                      'project_doc_max_bytes=0', 'web_search="disabled"', 'read-only',
                      'shell_tool', 'apps', 'plugins', 'memories', 'skip_host_skill_discovery']:
            assert token in command
        assert not any('labels' in token or 'hc001' in token or 'output-schema' in token for token in command)
