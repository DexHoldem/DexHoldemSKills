"""Isolation and response-contract tests for the paired history experiment."""
import json
import tempfile
from pathlib import Path

from history_ablation import command_for, parse_response, prompt_for, public_inputs


class TestHistoryIsolation:
    """Check that current/future labels and outputs cannot enter model inputs."""

    def test_public_allowlist(self) -> None:
        """Only past parsed states, allowed caches and images through target survive."""
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            for n in range(4):
                state = root/f's{n}'
                state.mkdir()
                (state/'00_capture.jpg').write_bytes(b'image')
                (state/'01_parsed_state.md').write_text(f'annotation {n}')
                (state/'answer.json').write_text('SECRET')
            (root/'s_current').symlink_to('s2')
            (root/'ground_truth.json').write_text('SECRET')
            (root/'action_sequence.json').write_text('workflow')
            (root/'hole_card_cache.json').write_text('cache')
            images, annotations = public_inputs(root)
            assert [p.parent.name for p in images] == ['s0', 's1', 's2']
            assert [p.relative_to(root).as_posix() for p in annotations] == [
                's0/01_parsed_state.md', 's1/01_parsed_state.md',
                'action_sequence.json', 'hole_card_cache.json']

    def test_no_context_in_ablated_prompt(self) -> None:
        """The no-annotation condition does not interpolate provided text files."""
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            (root/'perception_eval').mkdir()
            (root/'perception_eval/default_prompt.py').write_text(
                'DEFAULT_PROMPT = "Schema for `visual_summary.json`: schema Do not write null"')
            guidelines = root/'skills/dexholdem-v2-native/visual_guidelines'
            guidelines.mkdir(parents=True)
            (guidelines/'A.md').write_text('Shared rules')
            context = root/'action_sequence.json'
            context.write_text('UNIQUE_PRIOR_ANNOTATION')
            images = [root/'s0/00_capture.jpg', root/'s1/00_capture.jpg']
            with_context = prompt_for(root, images, [context], 'annotated')
            without_context = prompt_for(root, images, [context], 'images_only_history')
            assert 'UNIQUE_PRIOR_ANNOTATION' in with_context
            assert 'UNIQUE_PRIOR_ANNOTATION' not in without_context
            for prompt in (with_context, without_context):
                assert '1: s0/00_capture.jpg [HISTORY]' in prompt
                assert '2: s1/00_capture.jpg [CURRENT TARGET]' in prompt
                assert 'Shared rules' in prompt

    def test_command_has_all_images_and_no_tools(self) -> None:
        """Every chronological image is attached; sensitive tool classes disabled."""
        command = command_for('gpt-6-astra', Path('/tmp/task'), [Path('/tmp/a.jpg'), Path('/tmp/b.jpg')])
        assert [command[i+1] for i, arg in enumerate(command) if arg == '-i'] == ['/tmp/a.jpg', '/tmp/b.jpg']
        disabled = {command[i+1] for i, arg in enumerate(command) if arg == '--disable'}
        assert {'shell_tool', 'unified_exec', 'view_image', 'apps', 'browser_use', 'memories'} <= disabled
        assert '--ignore-rules' in command
        assert '--ephemeral' in command


class TestHistoryResponse:
    """Check final-message selection and failures without mocking a runner."""

    def test_final_message_and_usage(self) -> None:
        """Progress is retained, but only the final assistant JSON is scored."""
        events = [
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Inspecting images.'}},
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"table":{"scene_stable":false}}'}},
            {'type': 'turn.completed', 'usage': {'input_tokens': 42}}]
        record = parse_response('\n'.join(json.dumps(e) for e in events), 0)
        assert record['status'] == 'completed'
        assert record['prediction']['table']['scene_stable'] is False
        assert len(record['assistant_messages']) == 2
        assert record['usage']['input_tokens'] == 42

    def test_tool_use_is_rejected(self) -> None:
        """A valid answer cannot conceal an unauthorized tool invocation."""
        events = [
            {'type': 'item.started', 'item': {'type': 'command_execution'}},
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{}'}},
            {'type': 'turn.completed'}]
        assert parse_response('\n'.join(json.dumps(e) for e in events), 0)['status'] == 'unexpected_tool_access'

    def test_failure_and_invalid_json_are_distinct(self) -> None:
        """Execution failure and malformed final answer both remain unscored."""
        events = [
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '```json\n{}\n```'}},
            {'type': 'turn.completed'}]
        stdout = '\n'.join(json.dumps(e) for e in events)
        assert parse_response(stdout, 0)['status'] == 'invalid_json'
        assert parse_response(stdout, 1)['status'] == 'execution_error'
