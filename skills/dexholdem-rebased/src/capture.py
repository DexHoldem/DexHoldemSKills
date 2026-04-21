#!/usr/bin/env python3
"""Minimal local camera capture utility for texas-holdem-robot."""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Capture one frame from a local camera.")
    parser.add_argument("--device", type=int, default=0, help="Camera index to open.")
    parser.add_argument(
        "--output",
        default="/tmp/poker_latest.jpg",
        help="Path to write the captured image.",
    )
    args = parser.parse_args()

    try:
        import cv2
    except ImportError:
        print("Error: OpenCV is required. Install with: pip install opencv-python", file=sys.stderr)
        sys.exit(1)

    cap = cv2.VideoCapture(args.device)
    if not cap.isOpened():
        print(f"Error: could not open camera device {args.device}", file=sys.stderr)
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    ok, frame = cap.read()
    cap.release()

    if not ok or frame is None:
        print("Error: failed to read a frame from the camera", file=sys.stderr)
        sys.exit(1)

    output_path = os.path.abspath(args.output)
    if not cv2.imwrite(output_path, frame):
        print(f"Error: failed to write image to {output_path}", file=sys.stderr)
        sys.exit(1)

    print(output_path)


if __name__ == "__main__":
    main()
