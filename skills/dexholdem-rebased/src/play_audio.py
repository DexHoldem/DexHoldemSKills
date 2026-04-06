#!/usr/bin/env python3
"""Play an audio file from the audio/ directory in the background."""

import argparse
import os
import subprocess
import sys


AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio")


def main():
    parser = argparse.ArgumentParser(
        description="Play an audio file from the audio/ directory in the background."
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Audio filename (e.g. intro.mp3). Resolved relative to the audio/ directory.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available audio files and exit.",
    )
    args = parser.parse_args()

    if args.list:
        if not os.path.isdir(AUDIO_DIR):
            print("audio/ directory not found", file=sys.stderr)
            sys.exit(1)
        for f in sorted(os.listdir(AUDIO_DIR)):
            print(f)
        return

    if args.file is None:
        parser.error("the following arguments are required: file")

    path = os.path.join(AUDIO_DIR, args.file)
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Use afplay on macOS, otherwise fall back to ffplay (ffmpeg) or aplay
    if sys.platform == "darwin":
        cmd = ["afplay", path]
    else:
        # ffplay is widely available via ffmpeg; suppress output
        cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(proc.pid)


if __name__ == "__main__":
    main()
