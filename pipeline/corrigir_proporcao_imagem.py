#!/usr/bin/env python3
"""
AUT panel image aspect/scale guard.

Derived from user-provided corrigir_proporcao_imagem.py
source SHA-256: 835d2cf2293169fffd25b2f5279412e33500d6f7b05afffbe2cc8faeaa17ce31

Engineering invariant:
    GROW THE CANVAS; NEVER SHRINK OR DISTORT THE GEOMETRY.

This utility deliberately differs from generic "fit in frame" behavior:
for dimensional engineering images, a frame smaller than the source is an
error. The image is never squeezed, stretched, or uniformly downscaled just
to fit a fixed poster.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from PIL import Image

SOURCE_SHA256 = "835d2cf2293169fffd25b2f5279412e33500d6f7b05afffbe2cc8faeaa17ce31"


class AspectGuardError(RuntimeError):
    pass


def get_image_size(path: str | Path) -> tuple[int, int]:
    with Image.open(path) as img:
        return img.size


def aspect_ratio(width: int, height: int) -> float:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    return width / height


def required_frame_for_image(
    image_path: str | Path,
    min_width: int | None = None,
    min_height: int | None = None,
) -> tuple[int, int]:
    """Return a grow-only frame. Never scales the source image down."""
    width, height = get_image_size(image_path)
    target_w = max(width, min_width or width)
    target_h = max(height, min_height or height)
    return target_w, target_h


def verify_expected_ratio(
    image_path: str | Path,
    expected_width: float,
    expected_height: float,
    tolerance: float = 0.001,
) -> dict:
    width, height = get_image_size(image_path)
    actual = aspect_ratio(width, height)
    expected = expected_width / expected_height
    rel_error = abs(actual - expected) / max(abs(expected), 1e-12)
    return {
        "status": "PASS" if rel_error <= tolerance else "REPROVADO",
        "image_px": {"width": width, "height": height},
        "actual_ratio": actual,
        "expected_ratio": expected,
        "relative_error": rel_error,
        "tolerance": tolerance,
    }


def place_in_frame_grow_only(
    image_path: str | Path,
    output_path: str | Path,
    frame_width: int,
    frame_height: int,
    background: tuple[int, int, int, int] = (255, 255, 255, 0),
) -> dict:
    """
    Place the source at 1:1 pixels in a larger frame.

    No resize is performed. If the requested frame is smaller than the source,
    fail closed and report the minimum required frame.
    """
    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        width, height = img.size

        if frame_width < width or frame_height < height:
            raise AspectGuardError(
                f"requested frame {frame_width}x{frame_height} is smaller than "
                f"source {width}x{height}; grow canvas to at least {width}x{height}"
            )

        canvas = Image.new("RGBA", (frame_width, frame_height), background)
        offset_x = (frame_width - width) // 2
        offset_y = (frame_height - height) // 2
        canvas.paste(img, (offset_x, offset_y), img)
        canvas.save(output_path)

    return {
        "status": "PASS",
        "source_px": {"width": width, "height": height},
        "frame_px": {"width": frame_width, "height": frame_height},
        "scale_x": 1.0,
        "scale_y": 1.0,
        "offset_px": {"x": offset_x, "y": offset_y},
        "policy": "GROW_CANVAS_KEEP_SCALE",
    }


def parse_background(value: str | None) -> tuple[int, int, int, int]:
    if value is None:
        return (255, 255, 255, 0)
    parts = [int(p.strip()) for p in value.split(",")]
    if len(parts) == 3:
        parts.append(255)
    if len(parts) != 4 or any(p < 0 or p > 255 for p in parts):
        raise ValueError("--background must be R,G,B or R,G,B,A with values 0..255")
    return tuple(parts)  # type: ignore[return-value]


def emit(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)

    frame = sub.add_parser("frame-to-image", help="grow frame without shrinking source")
    frame.add_argument("image")
    frame.add_argument("--min-width", type=int)
    frame.add_argument("--min-height", type=int)
    frame.add_argument("--json", action="store_true")

    fit = sub.add_parser("fit-in-frame", help="place at 1:1 pixels; fail if frame is smaller")
    fit.add_argument("image")
    fit.add_argument("output")
    fit.add_argument("--frame-width", type=int, required=True)
    fit.add_argument("--frame-height", type=int, required=True)
    fit.add_argument("--background")
    fit.add_argument("--json", action="store_true")

    verify = sub.add_parser("verify", help="verify image aspect ratio against engineering dimensions")
    verify.add_argument("image")
    verify.add_argument("--expected-width", type=float, required=True)
    verify.add_argument("--expected-height", type=float, required=True)
    verify.add_argument("--tolerance", type=float, default=0.001)
    verify.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.mode == "frame-to-image":
            w, h = required_frame_for_image(args.image, args.min_width, args.min_height)
            src_w, src_h = get_image_size(args.image)
            emit({
                "status": "PASS",
                "source_px": {"width": src_w, "height": src_h},
                "frame_px": {"width": w, "height": h},
                "ratio": aspect_ratio(src_w, src_h),
                "scale_x": 1.0,
                "scale_y": 1.0,
                "policy": "GROW_CANVAS_KEEP_SCALE",
            }, args.json)
            return 0

        if args.mode == "fit-in-frame":
            result = place_in_frame_grow_only(
                args.image,
                args.output,
                args.frame_width,
                args.frame_height,
                parse_background(args.background),
            )
            emit(result, args.json)
            return 0

        result = verify_expected_ratio(
            args.image,
            args.expected_width,
            args.expected_height,
            args.tolerance,
        )
        emit(result, args.json)
        return 0 if result["status"] == "PASS" else 2
    except (AspectGuardError, ValueError) as exc:
        emit({"status": "REPROVADO", "error": str(exc), "policy": "GROW_CANVAS_KEEP_SCALE"}, True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
