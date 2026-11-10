"""Package exact ablated inputs, annotated-context overlay, and held-card data."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path

SECRET = re.compile(rb"AIza[\w-]{30,}|sk-or-v1-[a-f0-9]{64}")


def package(repo: Path, campaign: Path, held_card: Path, target: Path) -> dict:
    """Build and verify a ZIP without placing gold labels in model input folders.

    Args:
        repo (Path): Original source and annotated benchmark inputs.
        campaign (Path): Frozen ablated input copies and protocol manifest.
        held_card (Path): Separate held-card diagnostic package.
        target (Path): Output ZIP path.

    Returns:
        dict: ZIP checksum, bytes, and per-member content checksums.
    """
    protocol = json.loads((campaign / "protocol.json").read_text())
    members: dict[str, bytes] = {}
    links: set[str] = set()
    for problem, inputs in protocol["problems"].items():
        for relative, expected in inputs["retained"].items():
            path = campaign / "problems" / problem / relative
            name = f"no_annotated_history/problems/{problem}/{relative}"
            if "symlink" in expected:
                if str(path.readlink()) != expected["symlink"]:
                    raise ValueError("Current-state link changed")
                data = expected["symlink"].encode()
                links.add(name)
            else:
                data = path.read_bytes()
                if hashlib.sha256(data).hexdigest() != expected["sha256"]:
                    raise ValueError("Frozen input changed")
            members[name] = data
        for relative, expected in inputs["removed"].items():
            data = (repo / "bench/problems" / problem / relative).read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError("Original annotation changed")
            members[f"annotated_history_overlay/{problem}/{relative}"] = data
    for name in ("ground_truth.json", "problem_types.json"):
        members[f"reference_only/{name}"] = (repo / "bench/problems" / name).read_bytes()
    for path in held_card.rglob("*"):
        relative = path.relative_to(held_card)
        if "results" in relative.parts or "__pycache__" in relative.parts or not path.is_file():
            continue
        members[f"held_card_image_only_v1/{relative.as_posix()}"] = path.read_bytes()
    members["protocol.json"] = (campaign / "protocol.json").read_bytes()
    readme = """# DexHoldem reviewer input package

The 36-problem ablation uses the ORIGINAL native paper runner, prompt, tools,
output checks and scorer. Only annotated history and cached information are
removed. All 593 historical/current JPEGs and 36 s_current links are unchanged.
This is NOT a current-image-only benchmark: historical images remain available.

`no_annotated_history/problems/p1` ... `p36` are the exact model inputs. Removed:
557 previous-state 01_parsed_state.md files, 557 annotated 02_action.md files,
and 72 action_sequence.json / hole_card_cache.json files. The original prompt
still names these context files; the prompt was deliberately left unchanged.

`annotated_history_overlay` contains precisely those removed files. To restore
the original annotated inputs, copy the no_annotated_history/problems tree to
a DIFFERENT directory and overlay annotated_history_overlay onto that copy.
Images and current-state links are the same in both settings. Do not add this
overlay when running the ablation. The included restore script performs this
operation and refuses an existing destination.

`reference_only` contains gold labels and applicability metadata for OFFLINE
scoring. Never copy this directory into a model workspace.

`held_card_image_only_v1` is the separate 11-image, no-history diagnostic. It
includes its original inputs, scorer and private gold labels. Only inputs go
to models. Its gold labels are proposed_visual_review and require human review.
Do not merge its rank-and-suit score into the original 36-problem paper table.

ZIP symlink entries preserve s_current on Unix. If your extractor materializes
a symlink as a text file, replace it with the relative symlink recorded in
protocol.json. All per-file hashes, including link-target bytes, are in
INPUT_MANIFEST.json. No inference logs or credentials are in this input ZIP.
"""
    members["README.md"] = readme.encode()
    restore = '''"""Restore original annotated benchmark inputs from the exact overlay."""
from pathlib import Path
import argparse
import shutil


def main() -> None:
    """Create a separate annotated input tree; never modify the ablation tree."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    if args.destination.exists():
        raise ValueError("Destination already exists")
    shutil.copytree(base / "no_annotated_history/problems", args.destination, symlinks=True)
    shutil.copytree(base / "annotated_history_overlay", args.destination, dirs_exist_ok=True)


if __name__ == "__main__":
    main()
'''
    members["restore_annotated_inputs.py"] = restore.encode()
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in members.items()}
    manifest = {"files": hashes, "symlinks": sorted(links), "current_and_history_images": 593,
                "problems": 36, "labels_separate_from_inputs": True}
    members["INPUT_MANIFEST.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(members.items()):
            if not name.endswith((".jpg", ".png")) and SECRET.search(data):
                raise ValueError(f"Credential-like content in {name}; refusing export")
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = ((stat.S_IFLNK | 0o777) if name in links else (stat.S_IFREG | 0o644)) << 16
            info.compress_type = zipfile.ZIP_STORED if name.endswith(".jpg") else zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    with zipfile.ZipFile(target) as archive:
        for name, expected in hashes.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                raise ValueError("Input ZIP round-trip hash mismatch")
        if sum(stat.S_ISLNK(archive.getinfo(name).external_attr >> 16) for name in links) != 36:
            raise ValueError("Current-image link metadata missing")
    manifest.update(zip_sha256=hashlib.sha256(target.read_bytes()).hexdigest(), zip_bytes=target.stat().st_size,
                    round_trip_verified=True, credential_scan="passed")
    target.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    """Package user-authorized benchmark inputs for the project handoff."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "campaign", "held-card", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = package(args.repo, args.campaign, args.held_card, args.output)
    print(json.dumps({"members": len(report["files"]), "symlinks": len(report["symlinks"]),
                      "bytes": report["zip_bytes"], "sha256": report["zip_sha256"],
                      "round_trip_verified": report["round_trip_verified"]}))


if __name__ == "__main__":
    main()
