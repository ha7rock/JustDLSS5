"""Store artwork, resolved and decoded outside the UI thread.

Store identity wins; name search requires a clear, identity-compatible match.
No game executable is loaded, and a cover failure never blocks installation.
"""
import hashlib
import json
import os
import queue
import ssl
import certifi
import re
import time
import unicodedata
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .backend import covers as upstream_art

from PySide6.QtCore import QObject, QTimer, Signal, Qt, QRect
from PySide6.QtGui import QImage, QImageReader, QPainter, QColor


def normalized(title):
    title = title.replace("™", "").replace("®", "").replace("©", "")
    return "".join(c for c in unicodedata.normalize("NFKC", title).casefold() if c.isalnum())


def exact_match(items, title):
    matches = {str(i["id"]) for i in items if i.get("type", "app") == "app"
               and normalized(i.get("name", "")) == normalized(title)
               and str(i.get("id", "")).isdigit()}
    return next(iter(matches)) if len(matches) == 1 else None


def clean_name(title):
    """Remove packaging noise, preserving subtitles, sequel numbers and demos."""
    title = unicodedata.normalize("NFKC", title.replace("™", "").replace("®", ""))
    title = title.replace("_", " ")
    title = re.sub(r"\b(?:repack|fitgirl|dodi|elamigos|codex|rune|empress|plaza|skidrow|multi\d+)\b", " ", title, flags=re.I)
    title = re.sub(r"\bv\d+(?:\.\d+)+\b", " ", title, flags=re.I)
    title = re.sub(r"[\[\]()_\-–—:.]+", " ", title)
    return " ".join(title.split())


def match_title(title):
    title = clean_name(title).casefold()
    return re.sub(r"\s+(?:ultimate|deluxe|complete|definitive|standard|game of the year) edition$", "", title)


def identity_markers(title):
    return (tuple(re.findall(r"\d+|\b(?:ii|iii|iv|v|vi|vii|viii|ix|x)\b", title)),
            bool(re.search(r"\b(?:demo|prologue|playtest)\b|试玩|序章", title)))


def best_match(items, title):
    query = match_title(title)
    candidates = {str(i["id"]): match_title(i.get("name", "")) for i in items
                  if i.get("type", "app") == "app" and str(i.get("id", "")).isdigit()}
    exact = [key for key, name in candidates.items() if normalized(name) == normalized(query)]
    if exact:
        return exact[0] if len(exact) == 1 else None
    scores = []
    for key, name in candidates.items():
        if identity_markers(query) != identity_markers(name):
            continue
        a, b = normalized(query), normalized(name)
        # An added subtitle can be another game, even with a high similarity.
        if not a or not b or a in b or b in a:
            continue
        score = SequenceMatcher(None, a, b).ratio()
        scores.append((score, key))
    scores.sort(reverse=True)
    if scores and scores[0][0] >= .88 and (len(scores) == 1 or scores[0][0] - scores[1][0] >= .12):
        return scores[0][1]
    return None


def prepare_artwork(image):
    """Compose wide art once in the worker; painting never blurs or reads files."""
    if image.isNull() or image.width() <= image.height():
        return image
    canvas = QImage(400, 600, QImage.Format.Format_RGB32)
    expanded = image.scaled(400, 600, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                            Qt.TransformationMode.SmoothTransformation)
    crop = expanded.copy((expanded.width() - 400) // 2, (expanded.height() - 600) // 2, 400, 600)
    # Low-pass downsampling produces a soft backdrop without new dependencies.
    soft = crop.scaled(12, 18, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawImage(canvas.rect(), soft)
    painter.fillRect(canvas.rect(), QColor(0, 0, 0, 85))
    fitted = image.size().scaled(canvas.size(), Qt.AspectRatioMode.KeepAspectRatio)
    target = QRect(0, 0, fitted.width(), fitted.height())
    target.moveCenter(canvas.rect().center())
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawImage(target, image)
    painter.end()
    return canvas


def steam_id(game):
    folder = Path(game.folder)
    for parent in (folder, *folder.parents):
        if parent.name.casefold() != "steamapps":
            continue
        for manifest in parent.glob("appmanifest_*.acf"):
            try:
                text = manifest.read_text(encoding="utf8")
                directory = re.search(r'"installdir"\s+"([^"]+)"', text)
                app = re.search(r'"appid"\s+"(\d+)"', text)
                if directory and app and (parent / "common" / directory[1]).resolve() == folder.resolve():
                    return app[1]
            except OSError:
                continue
        break
    return None


def fetch(url, limit):
    request = Request(url, headers={"User-Agent": "JustDLSS5", "Accept-Language": "en"})
    with urlopen(request, timeout=6, context=ssl.create_default_context(cafile=certifi.where())) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Artwork response too large")
    return data


def read_image(path):
    reader = QImageReader(str(path))
    size = reader.size()
    if size.width() <= 0 or size.height() <= 0 or size.width() * size.height() > 24_000_000:
        return QImage()
    reader.setAutoTransform(True)
    image = reader.read()
    if image.isNull():
        return image
    return prepare_artwork(image.scaled(400, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))


def cache_directory():
    return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "JustDLSS5" / "covers"


def cache_key(game):
    return hashlib.sha256(str(game.folder).casefold().encode()).hexdigest()


def local_artwork(game, appid):
    """Use explicit artwork filenames only; never pick arbitrary screenshots."""
    folder = Path(game.folder)
    for stem in ("poster", "cover", "library_600x900"):
        for suffix in (".jpg", ".png", ".webp"):
            yield folder / (stem + suffix)
    if not appid:
        return
    roots = {p.parent for p in folder.parents if p.name.casefold() == "steamapps"}
    if os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                roots.add(Path(winreg.QueryValueEx(key, "SteamPath")[0]))
        except OSError:
            pass
    for root in roots:
        cache = root / "appcache/librarycache"
        for suffix in ("jpg", "png", "webp"):
            yield cache / f"{appid}_library_600x900.{suffix}"
            yield cache / appid / f"library_600x900.{suffix}"


def search_id(game):
    names = [game.name]
    folder_name = Path(game.folder).name
    if normalized(folder_name) != normalized(game.name):
        names.append(folder_name)
    for name in names:
        name = clean_name(name)
        if len(normalized(name)) < 3:
            continue
        for language in ("english", "schinese"):
            try:
                data = json.loads(fetch("https://store.steampowered.com/api/storesearch/?" +
                                        urlencode({"term": name, "cc": "us", "l": language}), 1_000_000))
                appid = best_match(data.get("items", []), name)
                if appid:
                    return appid
            except (OSError, ValueError):
                continue
    return None


def load_cover(game, custom="", network=True, cache=None):
    if custom:
        return read_image(custom)
    for artwork in (upstream_art.user(game), upstream_art.got(game), upstream_art.xbox(game.folder)):
        for kind in ("cover", "hero"):
            if kind in artwork:
                image = read_image(artwork[kind])
                if not image.isNull():
                    return image
    cache = cache or cache_directory()
    key = cache_key(game)
    target = cache / (key + ".jpg")
    cached = read_image(target) if target.is_file() else QImage()
    if not network and not cached.isNull():
        return cached
    appid = steam_id(game)
    for path in local_artwork(game, appid):
        if path.is_file():
            image = read_image(path)
            if not image.isNull():
                return image
    if not network:
        return QImage()
    # Upstream resolves Epic's official catalog and Steam's hashed asset paths.
    # Run it before the legacy negative cache, which may describe an old URL.
    upstream_art.lookup(game, appid=appid)
    art = upstream_art.got(game)
    for kind in ("cover", "hero"):
        if kind in art:
            image = read_image(art[kind])
            if not image.isNull():
                return image
    if not cached.isNull():
        return cached
    miss = cache / (key + ".missing-v3")
    if miss.exists() and time.time() - miss.stat().st_mtime < 86400:
        return QImage()
    if not appid:
        appid = search_id(game)
    cache.mkdir(parents=True, exist_ok=True)
    if appid:
        for name in ("library_600x900.jpg", "header.jpg"):
            try:
                data = fetch(f"https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/{appid}/{name}", 5_000_000)
                temp = cache / (key + ".part")
                temp.write_bytes(data)
                image = read_image(temp)
                if not image.isNull():
                    temp.replace(target)
                    return image
                temp.unlink(missing_ok=True)
            except (OSError, ValueError):
                continue
    miss.touch()
    return QImage()


class CoverLoader(QObject):
    ready = Signal(str, object)

    def __init__(self, parent=None, network=True):
        super().__init__(parent)
        self.network = network
        self.closed = False
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="covers")
        self.queue = queue.Queue()
        self.requested = set()
        self.pending = set()
        self.timer = QTimer(self)
        self.timer.setInterval(80)
        self.timer.timeout.connect(self.drain)
        self.timer.start()

    def request(self, entry, custom="", retry=False):
        if self.closed:
            return
        token = (entry.key, custom)
        if token in self.pending:
            return
        if token in self.requested and not retry:
            return
        self.requested.add(token)
        self.pending.add(token)
        def work():
            try:
                if retry:
                    upstream_art._write_meta(entry.game, {})
                    (cache_directory() / (cache_key(entry.game) + ".missing-v3")).unlink(missing_ok=True)
                image = load_cover(entry.game, custom, self.network)
            except Exception:
                image = QImage()
            self.queue.put((entry.key, custom, image))
        self.pool.submit(work)

    def drain(self):
        for _ in range(12):
            try:
                key, custom, image = self.queue.get_nowait()
            except queue.Empty:
                break
            self.pending.discard((key, custom))
            self.ready.emit(key, (custom, image))

    def shutdown(self):
        self.closed = True
        self.timer.stop()
        self.pool.shutdown(wait=False, cancel_futures=True)
