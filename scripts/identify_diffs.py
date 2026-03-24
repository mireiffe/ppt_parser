#!/usr/bin/env python3
"""Identify comparison images with significant rendering differences.

Reads side-by-side comparison PNGs from an input directory (default:
output/compare/), splits each into left (reference) and right (web render)
halves, computes the mean absolute pixel difference, and copies images that
exceed a threshold to an output directory (default: output/diff/).
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

LABEL_BAR_HEIGHT = 36
SEPARATOR_WIDTH = 4


def compute_pixel_diff(left_img: Image.Image, right_img: Image.Image) -> float:
    """Return the mean absolute pixel difference as a fraction in [0, 1]."""
    diff = ImageChops.difference(left_img, right_img)
    stat = ImageStat.Stat(diff)
    mean_diff = sum(stat.mean) / len(stat.mean)
    return mean_diff / 255.0


def process_image(img_path: Path, threshold: float) -> tuple[str, float, bool]:
    """Process a single comparison image.

    Returns (filename, diff_ratio, exceeds_threshold).
    """
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    mid = w // 2
    half_sep = SEPARATOR_WIDTH // 2

    left = img.crop((0, LABEL_BAR_HEIGHT, mid - half_sep, h))
    right = img.crop((mid + half_sep, LABEL_BAR_HEIGHT, w, h))

    target_w = min(left.width, right.width)
    target_h = min(left.height, right.height)
    if (left.width, left.height) != (target_w, target_h):
        left = left.resize((target_w, target_h), Image.LANCZOS)
    if (right.width, right.height) != (target_w, target_h):
        right = right.resize((target_w, target_h), Image.LANCZOS)

    diff = compute_pixel_diff(left, right)
    return img_path.name, diff, diff > threshold


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Identify comparison images with significant rendering differences."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("output/compare"),
        help="Directory containing comparison PNG images (default: output/compare)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/diff"),
        help="Directory to copy flagged images to (default: output/diff)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.05,
        help="Mean pixel difference threshold (0-1). Images above this are flagged (default: 0.05)",
    )
    args = parser.parse_args()

    input_dir: Path = args.input
    output_dir: Path = args.output
    threshold: float = args.threshold

    if not input_dir.is_dir():
        print(f"Error: Input directory not found: {input_dir}")
        raise SystemExit(1)

    png_files = sorted(input_dir.glob("*.png"))
    if not png_files:
        print(f"No PNG files found in {input_dir}")
        raise SystemExit(0)

    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[tuple[str, float, bool]] = []
    for img_path in png_files:
        name, diff, flagged = process_image(img_path, threshold)
        results.append((name, diff, flagged))

    flagged_results = [(n, d) for n, d, f in results if f]
    passed_results = [(n, d) for n, d, f in results if not f]

    print(f"Threshold: {threshold:.1%} mean pixel difference")
    print(f"Scanned:   {len(results)} images")
    print(f"Flagged:   {len(flagged_results)} images")
    print(f"Passed:    {len(passed_results)} images")
    print()

    if flagged_results:
        print("=== Flagged (significant differences) ===")
        for name, diff in sorted(flagged_results, key=lambda x: -x[1]):
            print(f"  {diff:6.2%}  {name}")
        print()

    if passed_results:
        print("=== Passed (within threshold) ===")
        for name, diff in sorted(passed_results, key=lambda x: -x[1]):
            print(f"  {diff:6.2%}  {name}")
        print()

    copied = 0
    for name, _diff, flagged in results:
        if flagged:
            shutil.copy2(input_dir / name, output_dir / name)
            copied += 1

    if copied:
        print(f"Copied {copied} flagged images to {output_dir}/")
    else:
        print("No images exceeded the threshold. Nothing copied.")


if __name__ == "__main__":
    main()
