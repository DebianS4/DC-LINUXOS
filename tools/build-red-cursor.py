#!/usr/bin/env python3
"""Build the DC-Red-Luminous Xcursor theme.

The artwork is intentionally generated from simple vector-like Pillow primitives,
so the repository contains no opaque binary source assets. xcursorgen writes the
final Xcursor files and preserves the hotspot for every requested size.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

SIZES = (24, 32, 48, 64)
RED = (255, 24, 40, 255)
RED_DARK = (172, 0, 18, 255)
HALO = (255, 255, 255, 210)
BLACK = (25, 25, 30, 255)

CURSOR_NAMES = {
    "left_ptr": "pointer",
    "default": "pointer",
    "arrow": "pointer",
    "hand": "hand",
    "pointer": "pointer",
    "text": "text",
    "xterm": "text",
    "crosshair": "crosshair",
    "wait": "wait",
    "progress": "progress",
    "move": "move",
    "size_all": "move",
    "h_double_arrow": "resize_h",
    "size_hor": "resize_h",
    "left_right": "resize_h",
    "v_double_arrow": "resize_v",
    "size_ver": "resize_v",
    "up_down": "resize_v",
    "not-allowed": "not_allowed",
    "forbidden": "not_allowed",
}

CANONICAL_KINDS = {"pointer", "hand", "text", "crosshair", "wait", "progress",
                   "move", "resize_h", "resize_v", "not_allowed"}


def pt(x: float, y: float, size: int) -> tuple[int, int]:
    return round(x * size / 64), round(y * size / 64)


def line(draw: ImageDraw.ImageDraw, points, size: int, fill, width: float = 1.0, joint="curve"):
    draw.line([pt(x, y, size) for x, y in points], fill=fill,
              width=max(1, round(width * size / 64)), joint=joint)


def polygon(draw: ImageDraw.ImageDraw, points, size: int, fill):
    draw.polygon([pt(x, y, size) for x, y in points], fill=fill)


def ellipse(draw: ImageDraw.ImageDraw, box, size: int, fill, outline=None, width: float = 1.0):
    draw.ellipse(tuple(v for xy in (pt(box[0], box[1], size), pt(box[2], box[3], size)) for v in xy),
                 fill=fill, outline=outline, width=max(1, round(width * size / 64)))


def base(size: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def pointer(size: int):
    image, draw = base(size)
    shape = [(7, 5), (7, 52), (19, 41), (27, 58), (34, 55), (25, 38), (42, 37)]
    polygon(draw, shape, size, HALO)
    inset = [(10, 10), (10, 45), (20, 35), (27, 50), (31, 48), (22, 33), (36, 33)]
    polygon(draw, inset, size, RED)
    line(draw, [(10, 10), (10, 45), (20, 35), (27, 50)], size, RED_DARK, 1.5)
    return image, (8, 8)


def hand(size: int):
    image, draw = base(size)
    # Open hand with a small, high-contrast halo.
    outline = [(22, 53), (17, 49), (17, 31), (20, 29), (23, 31), (23, 17),
               (26, 14), (29, 17), (29, 29), (31, 13), (34, 11), (37, 14),
               (36, 30), (38, 20), (41, 19), (43, 22), (40, 34), (44, 28),
               (47, 29), (48, 33), (42, 45), (36, 53)]
    polygon(draw, outline, size, HALO)
    inner = [(23, 50), (20, 47), (20, 32), (25, 32), (25, 19), (28, 18),
             (31, 33), (32, 16), (35, 15), (37, 34), (40, 23), (42, 23),
             (39, 39), (44, 32), (46, 33), (40, 45), (35, 50)]
    polygon(draw, inner, size, RED)
    line(draw, [(22, 52), (18, 48), (18, 31), (23, 29)], size, RED_DARK, 1.3)
    return image, (24, 28)


def text_cursor(size: int):
    image, draw = base(size)
    line(draw, [(22, 8), (22, 56)], size, HALO, 8)
    line(draw, [(22, 8), (22, 56)], size, RED, 4)
    line(draw, [(14, 10), (30, 10), (14, 54), (30, 54)], size, HALO, 4)
    line(draw, [(14, 10), (30, 10), (14, 54), (30, 54)], size, RED, 2)
    return image, (22, 32)


def crosshair(size: int):
    image, draw = base(size)
    ellipse(draw, (9, 9, 55, 55), size, None, HALO, 6)
    ellipse(draw, (11, 11, 53, 53), size, None, RED, 3)
    line(draw, [(32, 4), (32, 60)], size, HALO, 6)
    line(draw, [(4, 32), (60, 32)], size, HALO, 6)
    line(draw, [(32, 4), (32, 60)], size, RED, 2)
    line(draw, [(4, 32), (60, 32)], size, RED, 2)
    ellipse(draw, (28, 28, 36, 36), size, RED)
    return image, (32, 32)


def move(size: int):
    image, draw = base(size)
    line(draw, [(32, 5), (32, 59)], size, HALO, 9)
    line(draw, [(5, 32), (59, 32)], size, HALO, 9)
    polygon(draw, [(32, 4), (24, 17), (40, 17)], size, RED)
    polygon(draw, [(32, 60), (24, 47), (40, 47)], size, RED)
    polygon(draw, [(4, 32), (17, 24), (17, 40)], size, RED)
    polygon(draw, [(60, 32), (47, 24), (47, 40)], size, RED)
    ellipse(draw, (27, 27, 37, 37), size, RED_DARK)
    ellipse(draw, (29, 29, 35, 35), size, RED)
    return image, (32, 32)


def resize_cursor(size: int, horizontal: bool):
    image, draw = base(size)
    if horizontal:
        line(draw, [(5, 32), (59, 32)], size, HALO, 9)
        polygon(draw, [(4, 32), (18, 23), (18, 41)], size, RED)
        polygon(draw, [(60, 32), (46, 23), (46, 41)], size, RED)
    else:
        line(draw, [(32, 5), (32, 59)], size, HALO, 9)
        polygon(draw, [(32, 4), (23, 18), (41, 18)], size, RED)
        polygon(draw, [(32, 60), (23, 46), (41, 46)], size, RED)
    ellipse(draw, (28, 28, 36, 36), size, RED_DARK)
    return image, (32, 32)


def not_allowed(size: int):
    image, draw = base(size)
    ellipse(draw, (8, 8, 56, 56), size, HALO)
    ellipse(draw, (11, 11, 53, 53), size, RED)
    line(draw, [(19, 19), (45, 45)], size, HALO, 7)
    line(draw, [(19, 19), (45, 45)], size, RED_DARK, 3)
    return image, (32, 32)


def busy(size: int, frame: int, progress: bool):
    image, draw = base(size)
    # A compact glowing ring; progress rotates the lit segment per frame.
    cx = cy = size / 2
    radius = size * 0.30
    width = max(2, round(size * 0.11))
    for i in range(8):
        angle = (frame + i) % 8
        alpha = 255 if i == 0 else max(40, 220 - i * 25)
        import math
        a0 = math.radians(angle * 45 - 13)
        a1 = math.radians(angle * 45 + 13)
        box = (cx - radius, cy - radius, cx + radius, cy + radius)
        color = (255, 24, 40, alpha)
        draw.arc(tuple(round(v) for v in box), math.degrees(a0), math.degrees(a1), fill=HALO, width=width + 4)
        draw.arc(tuple(round(v) for v in box), math.degrees(a0), math.degrees(a1), fill=color, width=width)
    return image, (32, 32)


def artwork(kind: str, size: int, frame: int = 0):
    if kind == "pointer": return pointer(size)
    if kind == "hand": return hand(size)
    if kind == "text": return text_cursor(size)
    if kind == "crosshair": return crosshair(size)
    if kind == "move": return move(size)
    if kind == "resize_h": return resize_cursor(size, True)
    if kind == "resize_v": return resize_cursor(size, False)
    if kind == "not_allowed": return not_allowed(size)
    if kind == "wait": return busy(size, frame, False)
    if kind == "progress": return busy(size, frame, True)
    raise ValueError(kind)


def write_cursor(kind: str, output: Path, xcursorgen: str, frames: int = 1):
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dc-red-cursor-") as tmp:
        tmp_path = Path(tmp)
        config = tmp_path / "cursor.conf"
        pngs = []
        lines = []
        for frame in range(frames):
            for size in SIZES:
                image, hotspot = artwork(kind, size, frame)
                png = tmp_path / f"{kind}-{frame}-{size}.png"
                image.save(png, "PNG", optimize=True)
                pngs.append(png)
                delay = " 120" if frames > 1 else ""
                lines.append(f"{size} {hotspot[0] * size // 64} {hotspot[1] * size // 64} {png}{delay}\n")
        config.write_text("".join(lines), encoding="utf-8")
        target = output / kind
        subprocess.run([xcursorgen, str(config), str(target)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("config/includes.chroot/usr/share/icons/DC-Red-Luminous/cursors"))
    parser.add_argument("--xcursorgen", default=os.environ.get("XCURSORGEN", shutil.which("xcursorgen") or "xcursorgen"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for kind in sorted(CANONICAL_KINDS):
        write_cursor(kind, args.output, args.xcursorgen, frames=8 if kind in {"wait", "progress"} else 1)
    for name, target in CURSOR_NAMES.items():
        if name == target:
            continue
        link = args.output / name
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
