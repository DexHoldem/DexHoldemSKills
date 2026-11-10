"""Correctness checks for paired scoring and scene-level uncertainty."""
import json

from history_ablation import parse_response
from score_history import FIELDS, aggregate, answer_object, completed_response, paired_summary


class TestPairedScoring:
    """Check denominators and paired scene clustering against simple references."""

    def test_invalid_predictions_remain_in_denominators(self) -> None:
        """One correct and one failed trial yields one-half accuracy everywhere."""
        records = []
        for success in (True, False):
            records.append({'status': 'completed' if success else 'execution_error',
                            'overall': success, 'overall_plus_stability': success,
                            'fields': {c: success for c in FIELDS},
                            'stable_truth': True, 'stable_prediction': True if success else None})
        report = aggregate(records)
        assert report['overall'] == {'n': 2, 'correct': 1, 'accuracy': 0.5}
        assert report['field_macro_average'] == 0.5
        assert report['stability']['accuracy'] == 0.5
        assert report['stability']['missing_or_invalid'] == 1

    def test_field_average_is_macro_not_micro(self) -> None:
        """Unequal field denominators do not change the equal field weighting."""
        records = [
            {'status': 'completed', 'overall': False, 'overall_plus_stability': False,
             'fields': {c: c == 'stage' for c in FIELDS}, 'stable_truth': True, 'stable_prediction': True},
            {'status': 'completed', 'overall': True, 'overall_plus_stability': True,
             'fields': {'stage': True}, 'stable_truth': False, 'stable_prediction': False}]
        assert aggregate(records)['field_macro_average'] == 1/8

    def test_repeats_cluster_by_scene(self) -> None:
        """Six attempts on two scenes remain two clusters with zero mean delta."""
        records = []
        for pid, annotated, ablated in [('p1', True, False), ('p2', False, True)]:
            for repeat in (1, 2, 3):
                for condition, correct in [('annotated', annotated), ('images_only_history', ablated)]:
                    records.append({'condition': condition, 'problem': pid, 'repeat': repeat, 'overall': correct})
        report = paired_summary(records)
        assert report['pairs'] == 6
        assert report['scene_count'] == 2
        assert report['overall_difference'] == 0
        assert report['pair_counts'] == {'annotated_only': 3, 'ablated_only': 3}
        assert report['scene_mean_differences'] == {'p1': -1, 'p2': 1}
        assert report['scene_cluster_bootstrap_95_percentile'] == [-1, 1]

    def test_fence_normalization_is_narrow_and_separate(self) -> None:
        """Only one whole-response code fence can be removed; no answer selection."""
        record = {'status': 'invalid_json', 'result': '```json\n{"loop_stage":"idle"}\n```'}
        assert answer_object(record) is None
        assert answer_object(record, True) == {'loop_stage': 'idle'}
        for text in ['Explanation\n```json\n{}\n```', '{}{}', '```json\n{}{}\n```', '```json\n{}\n```\nMore text']:
            assert answer_object({'status': 'invalid_json', 'result': text}, True) is None
        assert answer_object({'status': 'model_mismatch', 'result': record['result']}, True) is None

    def test_successful_turn_after_reconnect_is_not_discarded(self) -> None:
        """A completed answer survives a reconnect notice but not a failed turn."""
        events = [{'type':'error','message':'Reconnecting... 2/5 (stream disconnected before completion: websocket closed)'},
                  {'type':'item.completed','item':{'type':'agent_message','text':'{"loop_stage":"idle"}'}},
                  {'type':'turn.completed'}]
        stdout = '\n'.join(json.dumps(e) for e in events)
        raw = parse_response(stdout, 0)
        assert raw['status'] == 'execution_error'
        effective, count = completed_response(raw, stdout, {'model':'gpt-6-sol'})
        assert effective['status'] == 'completed'
        assert effective['prediction'] == {'loop_stage':'idle'}
        assert count == 1
        failed = stdout+'\n'+json.dumps({'type':'turn.failed'})
        assert completed_response(raw, failed, {'model':'gpt-6-sol'}) == (raw, 0)
        other_error = stdout+'\n'+json.dumps({'type':'error','message':'Unauthorized model access'})
        assert completed_response(raw, other_error, {'model':'gpt-6-sol'}) == (raw, 0)
