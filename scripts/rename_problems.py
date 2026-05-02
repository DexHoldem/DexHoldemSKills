#!/usr/bin/env python3
"""Rename benchmark problems from scattered IDs to sequential p1-p36."""

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH_PROBLEMS = ROOT / "bench" / "problems"
BENCH_DESCRIPTIONS = ROOT / "bench" / "problem_descriptions"

# Mapping from old problem IDs to new sequential IDs
OLD_TO_NEW = {
    "p1": "p1", "p2": "p2", "p3": "p3", "p7": "p4", "p10": "p5",
    "p11": "p6", "p15": "p7", "p16": "p8", "p18": "p9", "p23": "p10",
    "p25": "p11", "p28": "p12", "p29": "p13", "p30": "p14", "p31": "p15",
    "p32": "p16", "p33": "p17", "p34": "p18", "p35": "p19", "p36": "p20",
    "p38": "p21", "p41": "p22", "p43": "p23", "p44": "p24", "p45": "p25",
    "p52": "p26", "p53": "p27", "p55": "p28", "p56": "p29", "p57": "p30",
    "p58": "p31", "p59": "p32", "p60": "p33", "p61": "p34", "p62": "p35",
    "p63": "p36",
}


def rename_with_temp(items: list[tuple[Path, Path]]) -> None:
    """Rename files/dirs via temp names to avoid collisions."""
    temp_map = []
    for src, dst in items:
        if src == dst:
            continue
        if not src.exists():
            print(f"  Skip (not found): {src}")
            continue
        temp = src.with_name(src.name + "_temp_rename")
        shutil.move(str(src), str(temp))
        temp_map.append((temp, dst))

    for temp, dst in temp_map:
        if dst.exists():
            print(f"  Warning: overwriting {dst}")
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
        shutil.move(str(temp), str(dst))
        print(f"  {temp.name.replace('_temp_rename', '')} -> {dst.name}")


def update_json_content(path: Path, old_to_new: dict[str, str]) -> None:
    """Update problem IDs and paths in JSON file."""
    text = path.read_text()

    # Replace problem_id values
    for old, new in old_to_new.items():
        # Match "problem_id": "pN" patterns
        text = re.sub(
            rf'"problem_id"\s*:\s*"{old}"',
            f'"problem_id": "{new}"',
            text
        )
        # Match "problem_dir": "bench/problems/pN" patterns
        text = re.sub(
            rf'"problem_dir"\s*:\s*"bench/problems/{old}"',
            f'"problem_dir": "bench/problems/{new}"',
            text
        )
        # Match capture paths
        text = re.sub(
            rf'"capture"\s*:\s*"bench/problems/{old}/',
            f'"capture": "bench/problems/{new}/',
            text
        )
        # Match bare problem IDs in arrays (e.g., ["p1", "p7", ...])
        text = re.sub(rf'"{old}"', f'"{new}"', text)

    path.write_text(text)


def main():
    print("=== Problem Renaming Script ===\n")

    # 1. Rename problem directories
    print("1. Renaming problem directories...")
    dir_renames = [
        (BENCH_PROBLEMS / old, BENCH_PROBLEMS / new)
        for old, new in OLD_TO_NEW.items()
    ]
    rename_with_temp(dir_renames)

    # 2. Rename problem JSON files
    print("\n2. Renaming problem JSON files...")
    json_renames = [
        (BENCH_PROBLEMS / f"{old}.json", BENCH_PROBLEMS / f"{new}.json")
        for old, new in OLD_TO_NEW.items()
    ]
    rename_with_temp(json_renames)

    # 3. Rename problem description files
    print("\n3. Renaming problem description files...")
    desc_renames = [
        (BENCH_DESCRIPTIONS / f"{old}.md", BENCH_DESCRIPTIONS / f"{new}.md")
        for old, new in OLD_TO_NEW.items()
    ]
    rename_with_temp(desc_renames)

    # 4. Update JSON content in individual problem files
    print("\n4. Updating individual problem JSON files...")
    for i in range(1, 37):
        json_file = BENCH_PROBLEMS / f"p{i}.json"
        if json_file.exists():
            update_json_content(json_file, OLD_TO_NEW)
            print(f"  Updated p{i}.json")

    # 5. Update ground_truth.json
    print("\n5. Updating ground_truth.json...")
    gt_file = BENCH_PROBLEMS / "ground_truth.json"
    if gt_file.exists():
        update_json_content(gt_file, OLD_TO_NEW)
        print("  Updated ground_truth.json")

    # 6. Update problem_types.json
    print("\n6. Updating problem_types.json...")
    pt_file = BENCH_PROBLEMS / "problem_types.json"
    if pt_file.exists():
        update_json_content(pt_file, OLD_TO_NEW)
        print("  Updated problem_types.json")

    # 7. Update problem_clusters.json
    print("\n7. Updating problem_clusters.json...")
    pc_file = BENCH_PROBLEMS / "problem_clusters.json"
    if pc_file.exists():
        update_json_content(pc_file, OLD_TO_NEW)
        print("  Updated problem_clusters.json")

    # 8. Regenerate core36_problem_list.txt
    print("\n8. Regenerating core36_problem_list.txt...")
    core36_file = BENCH_PROBLEMS / "core36_problem_list.txt"
    core36_file.write_text("\n".join(f"p{i}" for i in range(1, 37)) + "\n")
    print("  Generated p1-p36 list")

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
