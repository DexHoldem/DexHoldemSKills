"""Correctness checks for explicit stability extraction and fixed denominators."""
from evaluate_stability import metrics, parse_stability


class TestStabilityExtraction:
    """Keep stability independent from robot-stage predictions."""

    def test_explicit_values(self) -> None:
        """Both boolean values, their string forms and legacy root keys work."""
        for value, expected in [(True,True),(False,False),(' true ',True),('FALSE',False)]:
            assert parse_stability({'table':{'scene_stable':value}})==(expected,'valid')
            assert parse_stability({'scene_stable':value})==(expected,'valid')

    def test_no_stage_inference(self) -> None:
        """Stage labels cannot supply a missing stability answer."""
        for stage in ['acting','idle','down','atom_idle']:
            assert parse_stability({'loop_stage':stage})==(None,'missing_field')

    def test_invalid_and_conflicting(self) -> None:
        """Malformed values and conflicting aliases are not silently repaired."""
        for value in [None,1,0,[],{},'probably stable']:
            assert parse_stability({'table':{'scene_stable':value}})==(None,'invalid_field')
        assert parse_stability({'table':{'scene_stable':False},'scene_stable':True})==(None,'conflicting_fields')


class TestStabilityMetrics:
    """Validate counts against hand-computable reference cases."""

    def test_missing_denominators_and_confusion(self) -> None:
        """Missing values count as wrong without becoming false-stable predictions."""
        rows=[{'truth':t,'prediction':p} for t,p in [(True,True),(True,False),(True,None),(False,True),(False,False)]]
        result=metrics(rows)
        assert result['correct']==2 and result['n']==5 and result['accuracy']==2/5
        assert result['stable']['recall']==1/3 and result['unstable']['recall']==1/2
        assert result['balanced_accuracy']==(1/3+1/2)/2
        assert result['missing_or_invalid']==result['false_stable']==result['false_unstable']==1

    def test_imbalanced_reference(self) -> None:
        """Always-stable predictions cannot obtain high balanced accuracy."""
        result=metrics([{'truth':i<31,'prediction':True} for i in range(36)])
        assert result['accuracy']==31/36 and result['balanced_accuracy']==0.5
        assert result['unstable']['correct']==0 and result['false_stable']==5
