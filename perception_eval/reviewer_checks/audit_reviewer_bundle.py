"""Verify the extracted Slack result ZIP without the original ignored run folders."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_original import audit
from reviewer_handoff_report import audit_fields


def verify(bundle: Path) -> dict:
    """Audit original/new stability and both new paper-column result sets.

    Args:
        bundle (Path): Root of the extracted results-and-logs ZIP.

    Returns:
        dict: Independently verified trial and applicable-field counts.
    """
    repo = bundle / "source/original_native"
    result = {}
    for name in ("without_history", "with_history", "with_history_new_gpt"):
        scores = bundle / name / "scores"
        result[name] = audit(repo, scores)
        if name != "with_history":
            result[name]["fields"] = audit_fields(repo, scores)
    return result


def main() -> None:
    """Print reproducible verification counts from one extracted result bundle."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(verify(args.bundle), indent=2))


if __name__ == "__main__":
    main()
