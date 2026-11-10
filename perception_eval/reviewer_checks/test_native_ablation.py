"""Verify the corrected ablation changes input files only."""
import json
import tempfile
from pathlib import Path

import pytest

from native_ablation import command, digest, no_answer_quota, prepare_problem


class TestNativeAblation:
    """Keep image bytes, current-image links, original prompts and tool settings."""

    def test_removes_all_annotation_channels_without_changing_images(self) -> None:
        """Parsed states and action prose both contain annotated perception fields."""
        with tempfile.TemporaryDirectory() as work:
            root=Path(work);source=root/'source';source.mkdir()
            for index in (0,1):
                state=source/f's{index}';state.mkdir()
                (state/'00_capture.jpg').write_bytes(bytes([index,1,2,3]))
            (source/'s0/01_parsed_state.md').write_text('stage: idle')
            (source/'s0/02_action.md').write_text('The scene is stable')
            (source/'action_sequence.json').write_text('{}')
            (source/'hole_card_cache.json').write_text('{}')
            (source/'s_current').symlink_to('s1')
            (source/'runs').mkdir();(source/'runs/old-answer.json').write_text('{}')
            target=root/'target'
            result=prepare_problem(source,target)
            assert set(result['removed'])=={'s0/01_parsed_state.md','s0/02_action.md','action_sequence.json','hole_card_cache.json'}
            assert (target/'s_current').readlink()==Path('s1')
            assert not (target/'runs').exists()
            for index in (0,1):
                assert digest(source/f's{index}/00_capture.jpg')==digest(target/f's{index}/00_capture.jpg')
            for name in result['removed']:
                assert (source/name).exists() and not (target/name).exists()
            with pytest.raises(ValueError):
                prepare_problem(source,target)

    def test_calls_original_script_with_no_prompt_or_tool_override(self) -> None:
        """Only model/effort/run paths are passed to the existing paper runner."""
        for model,family in [('gpt-6-astra','codex'),('claude-opus-5-5','claude'),('gemini-3-flash-preview','gemini')]:
            cmd=command(Path('/repo'),Path('/out'),model,'p3','run1')
            assert cmd[1]==f'/repo/perception_eval/run_{family}_benchmark.py'
            assert cmd[cmd.index('--skill')+1]=='v2-native'
            assert '--prompt' not in cmd and '--prompt-file' not in cmd
            assert '--tools' not in cmd
            if family=='codex':
                assert cmd[-4:]==['--codex-disable','apps','--codex-disable','plugins']

    def test_quota_detection_requires_no_answer_and_zero_usage(self) -> None:
        """Do not retry an answered trial because its logs mention a quota."""
        with tempfile.TemporaryDirectory() as work:
            root=Path(work)
            data={'is_error':True,'result':"You've hit your 5-hour limit · resets 2:50am (Asia/Singapore)",
                  'usage':{'input_tokens':0,'output_tokens':0}}
            (root/'claude_stdout.txt').write_text(json.dumps(data))
            assert no_answer_quota(root,'claude')==data['result']
            (root/'visual_summary.json').write_text('{}')
            assert no_answer_quota(root,'claude') is None
            assert no_answer_quota(root,'codex') is None
