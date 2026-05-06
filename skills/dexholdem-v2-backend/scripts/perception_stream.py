#!/usr/bin/env python3
"""DexHoldem background perception stream helper."""

import argparse
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from utils import atomic_copy, atomic_write_json, current_state_name, extract_json_objects


STREAM_DIR_RE = "s_v"


def utc_now():
    return datetime.now(timezone.utc)


def parse_iso(value):
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def resolve_exp_dir(path=None):
    if path:
        return Path(path).resolve()
    cwd = Path.cwd()
    if (cwd / "s_current").exists() or (cwd / "hole_card_cache.json").exists():
        return cwd.resolve()
    current = cwd / "experiments" / "current"
    if current.exists():
        return current.resolve()
    raise RuntimeError("run from an experiment root or pass --exp-dir")


def stream_root(exp_dir, root=None):
    if root:
        return Path(root).resolve()
    key = hashlib.sha256(str(Path(exp_dir).resolve()).encode("utf-8")).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / "dexholdem_perception_stream" / key


def stream_index(path):
    name = Path(path).name
    if not name.startswith(STREAM_DIR_RE):
        return None
    suffix = name[len(STREAM_DIR_RE) :]
    return int(suffix) if suffix.isdigit() else None


def stream_dirs(root):
    root = Path(root)
    if not root.exists():
        return []
    found = []
    for path in root.iterdir():
        if not path.is_dir():
            continue
        index = stream_index(path)
        if index is not None:
            found.append((index, path))
    return [path for _, path in sorted(found, key=lambda item: item[0])]


def latest_complete(root):
    for path in reversed(stream_dirs(root)):
        manifest_path = path / "manifest.json"
        capture_path = path / "00_capture.jpg"
        parsed_path = path / "01_parsed_state.md"
        if not (manifest_path.exists() and capture_path.exists() and parsed_path.exists()):
            continue
        try:
            manifest = json.loads(manifest_path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if manifest.get("status") != "complete":
            continue
        try:
            blocks = extract_json_objects(parsed_path.read_text())
        except OSError:
            continue
        if not any(isinstance(block, dict) and isinstance(block.get("table"), dict) for block in blocks):
            continue
        return path, manifest
    return None, None


def replace_symlink(link, target):
    link = Path(link)
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(target)


def cmd_root(args):
    exp_dir = resolve_exp_dir(args.exp_dir)
    root = stream_root(exp_dir, args.stream_root)
    if args.mkdir:
        root.mkdir(parents=True, exist_ok=True)
    print(json.dumps({"exp_dir": str(exp_dir), "stream_root": str(root)}, indent=2))


def cmd_next_dir(args):
    exp_dir = resolve_exp_dir(args.exp_dir)
    root = stream_root(exp_dir, args.stream_root)
    root.mkdir(parents=True, exist_ok=True)
    existing = stream_dirs(root)
    next_index = stream_index(existing[-1]) + 1 if existing else 0
    path = root / f"s_v{next_index}"
    path.mkdir()
    manifest = {
        "schema_version": 1,
        "status": "in_progress",
        "exp_dir": str(exp_dir),
        "current_state": current_state_name(exp_dir),
        "created_at": utc_now().isoformat(),
    }
    atomic_write_json(path / "manifest.json", manifest)
    print(json.dumps({"stream_root": str(root), "stream_state": path.name, "stream_dir": str(path)}, indent=2))


def cmd_latest(args):
    exp_dir = resolve_exp_dir(args.exp_dir)
    root = stream_root(exp_dir, args.stream_root)
    path, manifest = latest_complete(root)
    if path is None:
        raise SystemExit(f"no complete perception stream state found under {root}")
    print(json.dumps({"stream_root": str(root), "stream_state": path.name, "stream_dir": str(path), "manifest": manifest}, indent=2))


def cmd_publish_latest(args):
    exp_dir = resolve_exp_dir(args.exp_dir)
    root = stream_root(exp_dir, args.stream_root)
    path = Path(args.stream_dir).resolve()
    manifest_path = path / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("status") != "complete":
        raise SystemExit(f"stream state is not complete: {path}")
    root.mkdir(parents=True, exist_ok=True)
    replace_symlink(root / "latest", path)
    atomic_write_json(root / "latest.json", {"stream_dir": str(path), "published_at": utc_now().isoformat()})
    print(json.dumps({"status": "ok", "latest": str(path)}, indent=2))


def cmd_import_latest(args):
    exp_dir = resolve_exp_dir(args.exp_dir)
    root = stream_root(exp_dir, args.stream_root)
    path, manifest = latest_complete(root)
    if path is None:
        raise SystemExit(f"no complete perception stream state found under {root}")

    expected_exp = str(exp_dir)
    if not args.allow_exp_mismatch and manifest.get("exp_dir") not in (None, expected_exp):
        raise SystemExit(f"latest stream exp_dir mismatch: {manifest.get('exp_dir')} != {expected_exp}")

    state_name = current_state_name(exp_dir)
    if not args.allow_state_mismatch and manifest.get("current_state") not in (None, state_name):
        raise SystemExit(f"latest stream state mismatch: {manifest.get('current_state')} != {state_name}")

    if not args.allow_stale:
        captured_at = parse_iso(manifest.get("captured_at"))
        parsed_at = parse_iso(manifest.get("parsed_at"))
        newest = max([value for value in (captured_at, parsed_at) if value is not None], default=None)
        if newest is None:
            raise SystemExit("latest stream manifest has no valid captured_at or parsed_at timestamp")
        age = (utc_now() - newest).total_seconds()
        if age > args.max_age_seconds:
            raise SystemExit(f"latest stream state is stale: {age:.1f}s > {args.max_age_seconds}s")

    state_dir = exp_dir / state_name
    capture_dest = state_dir / "00_capture.jpg"
    parsed_dest = state_dir / "01_parsed_state.md"
    if not args.overwrite:
        existing = [str(path) for path in (capture_dest, parsed_dest) if path.exists()]
        if existing:
            raise SystemExit(f"refusing to overwrite existing state files: {', '.join(existing)}")

    atomic_copy(path / "00_capture.jpg", capture_dest)
    atomic_copy(path / "01_parsed_state.md", parsed_dest)
    source_meta = {
        "schema_version": 1,
        "source": "perception_stream",
        "stream_root": str(root),
        "stream_state": path.name,
        "stream_dir": str(path),
        "manifest": manifest,
        "imported_at": utc_now().isoformat(),
    }
    atomic_write_json(state_dir / "perception_stream_import.json", source_meta)
    print(json.dumps({"status": "ok", "state": state_name, "imported_from": str(path)}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exp-dir", help="Experiment root. Defaults to cwd or experiments/current.")
    parser.add_argument("--stream-root", help="Override the /tmp perception stream root.")
    sub = parser.add_subparsers(dest="command", required=True)

    root_parser = sub.add_parser("root", help="Print the stream root for an experiment.")
    root_parser.add_argument("--mkdir", action="store_true")
    root_parser.set_defaults(func=cmd_root)

    next_parser = sub.add_parser("next-dir", help="Create and print the next s_vN stream folder.")
    next_parser.set_defaults(func=cmd_next_dir)

    latest_parser = sub.add_parser("latest", help="Print the latest complete stream state.")
    latest_parser.set_defaults(func=cmd_latest)

    publish_parser = sub.add_parser("publish-latest", help="Publish a completed stream folder as latest.")
    publish_parser.add_argument("stream_dir")
    publish_parser.set_defaults(func=cmd_publish_latest)

    import_parser = sub.add_parser("import-latest", help="Import latest complete stream state into s_current.")
    import_parser.add_argument("--max-age-seconds", type=float, default=90.0)
    import_parser.add_argument("--allow-stale", action="store_true")
    import_parser.add_argument("--allow-exp-mismatch", action="store_true")
    import_parser.add_argument("--allow-state-mismatch", action="store_true")
    import_parser.add_argument("--overwrite", action="store_true")
    import_parser.set_defaults(func=cmd_import_latest)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
