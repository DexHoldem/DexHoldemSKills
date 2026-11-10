"""Archive complete native model outputs and every preserved runner attempt."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
from pathlib import Path


def export(root: Path, output: Path) -> dict:
    """Archive verified complete models, refusing symlink escapes and credentials.

    Args:
        root (Path): Campaign directory containing records and raw runs.
        output (Path): Existing completed-model score directory.

    Returns:
        dict: Relative file hashes, model list and compressed archive checksum.
    """
    report = json.loads((output / "summary.json").read_text())
    files: set[Path] = set()
    runs: set[Path] = set()
    for row in report["models"]:
        records = root / "records" / row["model"]
        for path in records.rglob("*"):
            if path.is_file():
                files.add(path)
            if path.is_file() and path.name in {"record.json", "record_before_google_api.json"}:
                data = json.loads(path.read_text())
                if data.get("run_dir"):
                    runs.add(Path(data["run_dir"]))
    for run in runs:
        run.relative_to(root / "problems")
        if run.is_dir():
            files.update(p for p in run.rglob("*") if p.is_file())
    hashes = {}
    secret_pattern = re.compile(rb"AIza[\w-]{30,}|sk-or-v1-[a-f0-9]{64}")
    for path in sorted(files):
        path.resolve().relative_to(root.resolve())
        if path.is_symlink():
            raise ValueError("Raw archive contains a symlink; inspect before publishing")
        data = path.read_bytes()
        if secret_pattern.search(data):
            raise ValueError(f"Credential-like content detected in {path.name}; refusing export")
        hashes[str(path.relative_to(root))] = hashlib.sha256(data).hexdigest()
    archive = output / "raw_runs_and_attempts.tar.gz"
    with tarfile.open(archive, "w:gz") as bundle:
        for path in sorted(files):
            bundle.add(path, arcname=str(path.relative_to(root)), recursive=False)
    with tarfile.open(archive) as bundle:
        for name, expected in hashes.items():
            stream = bundle.extractfile(name)
            if stream is None or hashlib.sha256(stream.read()).hexdigest() != expected:
                raise ValueError("Archive round-trip hash mismatch")
    manifest = {"models": [r["model"] for r in report["models"]],
                "files": hashes, "run_directories": len(runs),
                "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "archive_bytes": archive.stat().st_size,
                "credential_scan": "passed", "round_trip_verified": True}
    (output / "raw_archive_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    """Export a completed-model checkpoint and report compact verification counts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = export(args.root.resolve(), args.output.resolve())
    print(json.dumps({"models": len(result["models"]), "files": len(result["files"]),
                      "raw_runs": result["run_directories"], "archive_bytes": result["archive_bytes"],
                      "round_trip_verified": result["round_trip_verified"]}))


if __name__ == "__main__":
    main()
