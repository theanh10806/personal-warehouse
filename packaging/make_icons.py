"""Turn ONE picture into every icon the project needs.

    python packaging/make_icons.py path\\to\\my_icon.png

Writes (commit all of them, so anyone who downloads the project from GitHub gets the icon too):
  src/personal_warehouse/webui/static/icon.png   - window sidebar + browser tab favicon
  src/personal_warehouse/webui/static/icon.ico   - Windows .exe / installer / taskbar (16..256 px)
  packaging/Assets/*.png                          - Microsoft Store (MSIX) tiles
Use a square PNG of at least 512x512 with a transparent background if you can. Needs Pillow (pip install pillow).
"""
from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "src" / "personal_warehouse" / "webui" / "static"
ASSETS = ROOT / "packaging" / "Assets"
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def square(im, side):
    """Fit the picture inside a transparent square (never crops or stretches it)."""
    im = im.convert("RGBA")
    scale = side / max(im.size)
    im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    return canvas


def main(src):
    base = Image.open(src)
    if min(base.size) < 256:
        print(f"Warning: {src} is only {base.size[0]}x{base.size[1]}; 512x512 or more gives a sharper icon.")
    big = square(base, max(512, min(1024, max(base.size))))
    STATIC.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    square(big, 512).save(STATIC / "icon.png")
    big.save(STATIC / "icon.ico", sizes=ICO_SIZES)
    for name, side in (("Square44x44Logo", 44), ("Square150x150Logo", 150), ("StoreLogo", 50), ("LargeTile", 310)):
        square(big, side).save(ASSETS / f"{name}.png")
    wide = Image.new("RGBA", (310, 150), (0, 0, 0, 0))
    wide.paste(square(big, 130), (90, 10))
    wide.save(ASSETS / "Wide310x150Logo.png")
    print("Done: icon.png, icon.ico and the Microsoft Store tiles were written.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_file():
        sys.exit(__doc__)
    main(sys.argv[1])
