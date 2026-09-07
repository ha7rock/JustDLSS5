"""Read icon resources in scan workers without loading executable code."""
import ctypes
from ctypes import wintypes
from functools import lru_cache
from pathlib import Path
from PySide6.QtGui import QImage


def usable_image(image):
    if image is None or image.isNull():
        return False
    if not image.hasAlphaChannel():
        return True
    # Some EXEs provide a non-null but entirely transparent first icon.
    rgba = image.convertToFormat(QImage.Format.Format_RGBA8888)
    return any(bytes(rgba.constBits())[3::4])


@lru_cache(maxsize=512)
def _extract(path, modified, size):
    extract = ctypes.windll.shell32.ExtractIconExW
    extract.argtypes = [wintypes.LPCWSTR, ctypes.c_int, ctypes.POINTER(wintypes.HICON), ctypes.POINTER(wintypes.HICON), ctypes.c_uint]
    extract.restype = ctypes.c_uint
    destroy = ctypes.windll.user32.DestroyIcon
    destroy.argtypes = [wintypes.HICON]
    large, small = wintypes.HICON(), wintypes.HICON()
    try:
        extract(path, 0, ctypes.byref(large), ctypes.byref(small), 1)
        for handle in (large, small):
            if handle.value:
                image = QImage.fromHICON(handle.value).copy()
                if usable_image(image):
                    return image
    finally:
        for value in {large.value, small.value} - {None, 0}:
            destroy(wintypes.HICON(value))
    # lru_cache does not cache exceptions: transient failures retry next scan.
    raise OSError("No usable icon resource")


def executable_icon(path):
    if not path:
        return None
    try:
        path = Path(path)
        stat = path.stat()
        return _extract(str(path), stat.st_mtime_ns, stat.st_size)
    except (OSError, AttributeError, ValueError):
        return None


def game_icon(game):
    image = executable_icon(game.exe)
    if usable_image(image):
        return image
    # Games may run a binary with no icon while their launcher owns the icon.
    candidates = list(dict.fromkeys(game.candidates or []))
    for candidate in candidates[:8]:
        if candidate == game.exe:
            continue
        image = executable_icon(candidate)
        if usable_image(image):
            return image
    paths = ([Path(game.exe).with_suffix(".ico")] if game.exe else [])
    paths += [Path(game.folder) / name for name in ("icon.ico", "game.ico")]
    for path in paths:
        if path.is_file():
            image = QImage(str(path))
            if usable_image(image):
                return image
    return None
