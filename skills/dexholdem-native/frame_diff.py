#!/usr/bin/env python3
"""
Pixel-level frame comparison utility for termination detection.

Usage: python3 frame_diff.py <image_a> <image_b>

Prints a float 0.0-1.0 (mean normalized pixel difference) to stdout.
Exit 0 on success, non-zero on failure.
"""

import sys

def compute_diff(path_a, path_b):
    """Compute mean normalized pixel difference between two images."""
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
        return None

    try:
        img_a = Image.open(path_a).convert("L")
        img_b = Image.open(path_b).convert("L")
    except Exception as e:
        print(f"Error: failed to open images: {e}", file=sys.stderr)
        return None

    # Resize to match if dimensions differ
    if img_a.size != img_b.size:
        img_b = img_b.resize(img_a.size, Image.LANCZOS)

    pixels_a = list(img_a.getdata())
    pixels_b = list(img_b.getdata())

    total_diff = sum(abs(a - b) for a, b in zip(pixels_a, pixels_b))
    mean_diff = total_diff / (len(pixels_a) * 255.0)

    return mean_diff


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <image_a> <image_b>", file=sys.stderr)
        sys.exit(1)

    result = compute_diff(sys.argv[1], sys.argv[2])
    if result is not None:
        print(f"{result:.6f}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
