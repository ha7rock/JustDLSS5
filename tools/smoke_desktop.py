"""Start the packaged app with isolated preferences; verify and close only its own window."""
import ctypes
from ctypes import wintypes
import os
import json
from pathlib import Path
import subprocess
import tempfile
import time
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from frontend.about import VERSION


def main():
    exe = Path(os.environ.get("STUDIO_DIST_DIR", ROOT / "dist" / ("v" + VERSION))) / "JustDLSS5/JustDLSS5.exe"
    user32 = ctypes.windll.user32
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    with tempfile.TemporaryDirectory(prefix="studio-smoke-") as temp:
        env = dict(os.environ, LOCALAPPDATA=temp)
        settings = Path(temp) / "dlss5-autopilot/settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text(json.dumps({"product_update_check": False}), encoding="utf8")
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        process = subprocess.Popen([str(exe)], env=env, startupinfo=startup)
        windows = []
        def visit(hwnd, data):
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value == process.pid:
                title = ctypes.create_unicode_buffer(512)
                user32.GetWindowTextW(hwnd, title, len(title))
                if title.value:
                    windows.append((hwnd, title.value))
            return True
        callback = callback_type(visit)
        deadline = time.monotonic() + 10
        success = False
        while time.monotonic() < deadline and process.poll() is None:
            windows.clear()
            user32.EnumWindows(callback, 0)
            if any("JustDLSS5" in title for _, title in windows):
                success = True
                break
            if any("exception" in title.lower() for _, title in windows):
                break
            time.sleep(.1)
        # Hardware detection runs briefly on startup; wait for orderly close.
        for _ in range(40):
            for hwnd, title in windows:
                if "JustDLSS5" in title or "exception" in title.lower():
                    user32.PostMessageW(hwnd, 0x0010, 0, 0)
            if process.poll() is not None:
                break
            time.sleep(.15)
        if process.poll() is None:
            process.terminate()  # Only this test-owned, idle application.
            process.wait(timeout=5)
            raise RuntimeError("Packaged application did not close cleanly")
        if not success or process.returncode != 0:
            raise RuntimeError(f"Packaged startup failed: {windows}; exit={process.returncode}")
        print("PASS: packaged JustDLSS5 created its window and exited cleanly.")


if __name__ == "__main__":
    main()
