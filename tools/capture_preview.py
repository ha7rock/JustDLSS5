"""Render a documentation screenshot using offline fixtures, never personal data."""
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from core import prefs
from frontend.desktop import MainWindow
from test_ui import FakeService, entry


def main():
    app = QApplication([])
    app.setStyle("Fusion")
    app.setFont(QFont("Microsoft YaHei UI", 10))
    with tempfile.TemporaryDirectory() as temp, patch.object(prefs, "FILE", Path(temp) / "prefs.json"):
        service = FakeService()
        service.entries = [entry("示例游戏 A"), entry("示例游戏 B", True), entry("示例游戏 C")]
        window = MainWindow(service=service, background=False)
        window.resize(1440, 900)
        window.show()
        window._scanned(service.entries)
        window.table.selectRow(0)
        for _ in range(100):
            QTest.qWait(20)
            if not window.jobs.active:
                break
        if window.jobs.active:
            raise RuntimeError("Preview fixture did not finish")
        window.status.setText("界面展示 · 示例数据")
        app.processEvents()
        destination = ROOT / "docs/images/library.zh-CN.png"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not window.grab().save(str(destination)):
            raise RuntimeError("Could not save screenshot")
        window.close()


if __name__ == "__main__":
    main()
