"""Generate the TRAKKNAME icon with Pillow (TRAKKOUT family style).

Design: amber circle (brand accent #F5A623) + white diagonal slash
(music/play gesture) + dark notch detail. Transparent background.
Outputs multi-size .ico (Windows) + .png (docs, taskbar fallback).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

AMBER = (245, 166, 35, 255)
WHITE = (255, 255, 255, 255)
DARK = (21, 22, 23, 255)

OUT_DIR = Path(__file__).resolve().parents[1] / "app" / "resources"
SIZE = 256


def draw(size: int = SIZE) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 256  # scale factor
    cx = cy = size / 2
    r = 118 * s
    # amber disc
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER)
    # subtle inner ring for depth
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(214, 144, 29, 255), width=max(2, int(5 * s)))
    # white diagonal slash (bottom-left -> top-right), music gesture
    w = 34 * s
    d.line([(cx - 62 * s, cy + 72 * s), (cx + 62 * s, cy - 72 * s)], fill=WHITE, width=int(w), joint="curve")
    # dark notch dot (needle-drop detail), lower-right of the slash
    nr = 17 * s
    nx, ny = cx + 44 * s, cy + 40 * s
    d.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=DARK)
    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = draw()
    ico = OUT_DIR / "trakkname.ico"
    img.save(ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    png = OUT_DIR / "trakkname.png"
    img.save(png)
    print(f"wrote {ico} ({ico.stat().st_size:,} bytes)")
    print(f"wrote {png} ({png.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
