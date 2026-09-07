"""Render the editable SVG into a Windows ICO with explicit small-size images."""
from pathlib import Path
import struct

from PySide6.QtCore import QByteArray, QBuffer, QIODevice, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parents[1]
SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)


def main():
    renderer = QSvgRenderer(str(ROOT / "frontend/justdlss5.svg"))
    if not renderer.isValid():
        raise RuntimeError("Invalid application icon SVG")
    frames = []
    for size in SIZES:
        canvas = QImage(size, size, QImage.Format.Format_ARGB32)
        canvas.fill(Qt.GlobalColor.transparent)
        painter = QPainter(canvas)
        renderer.render(painter)
        painter.end()
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not canvas.save(buffer, "PNG"):
            raise RuntimeError("PNG encoder unavailable")
        frames.append(bytes(data))
        if size == 256:
            destination = ROOT / "docs/images/app-icon.png"
            destination.parent.mkdir(parents=True, exist_ok=True)
            canvas.save(str(destination))
    header = struct.pack("<HHH", 0, 1, len(frames))
    offset = 6 + 16 * len(frames)
    for size, data in zip(SIZES, frames):
        header += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    (ROOT / "frontend/justdlss5.ico").write_bytes(header + b"".join(frames))


if __name__ == "__main__":
    main()
