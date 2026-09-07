"""Presentation-neutral operations. All filesystem/network work runs off the UI thread."""
from dataclasses import dataclass, replace, field
from pathlib import Path
from stat import S_ISREG

from .backend import games, gpu, dlss, installer, components, diagnose, video, sources, anticheat, mfg


@dataclass
class LibraryEntry:
    game: object
    installed: bool
    anticheat: str = ""
    icon_image: object = None

    @property
    def key(self):
        return str(self.game.folder).casefold()


@dataclass
class Inspection:
    entry: LibraryEntry
    support: object
    fit: dict
    options: object
    gpu_name: str
    level: str
    explanation: str
    levels: dict = field(default_factory=dict)
    api_override: str = ""
    mfg_available: bool = False


class BackendService:
    def __init__(self):
        self._gpu = None

    def hardware(self):
        if self._gpu is None:
            self._gpu = gpu.detect()
        return self._gpu

    def scan(self, emit):
        found = games.scan_all(progress=lambda text: emit("log", text))
        known = video.known()
        if known and not any(g.folder == known.folder for g in found):
            found.append(known)
        entries = []
        for game in found:
            if self.has_game_files(game):
                entries.append(self.decorate(game))
            else:
                emit("log", f"跳过残留目录（无游戏程序） / Skipped folder without a game executable: {game.folder}")
        return entries

    @staticmethod
    def has_game_files(game):
        if game.exe:
            try:
                if S_ISREG(Path(game.exe).stat().st_mode):
                    return True
            except PermissionError:
                # Store-managed games can be present but unreadable.
                return True
            except OSError:
                pass
        # Keep our remaining components accessible for uninstall/recovery.
        return bool(game.installed)

    def manual(self, path):
        game = games.manual(Path(path))
        if not game.exe:
            raise ValueError("未找到游戏程序 / No game executable found")
        return self.decorate(game)

    def decorate(self, game):
        from .icons import game_icon
        return LibraryEntry(game, bool(game.installed),
                            anticheat.detect(game.install_dir, game.folder).summary,
                            game_icon(game))

    def select_executable(self, entry, path):
        game = replace(entry.game, exe=Path(path), candidates=[Path(path)],
                       emu=None, install_root=None, error="")
        games.enrich(game)
        game.candidates = list(entry.game.candidates)
        return self.decorate(game)

    def inspect(self, entry):
        game = entry.game
        name, sm = self.hardware()
        support = dlss.detect(game.install_dir, game.folder, game.api, game.bitness or 0, sm)
        fit = {route: dlss.fit(route, game.api, support.native_dlss, sm,
                              upscaler=support.upscaler) for route in support.options}
        options = installer.options_from_manifest(game.install_dir) if entry.installed else None
        if options is None:
            options = installer.Options(path=support.recommended, native_dlss=support.native_dlss,
                                        upscaler=support.upscaler, dxvk=bool(installer.wants_dxvk(game)))
        else:
            options = replace(options, native_dlss=support.native_dlss, upscaler=support.upscaler)
        level, explanation = installer.reliability(game, options.path, upscaler=support.upscaler)
        levels = {route: installer.reliability(game, route, upscaler=support.upscaler)
                  for route in support.options}
        return Inspection(entry, support, fit, options, name or "", level, explanation, levels,
                          games.api_override(game.folder),
                          mfg.applies(sm, game.api, game.install_dir, game.folder)[0])

    def set_graphics_api(self, entry, api):
        if api and api not in games.APIS:
            raise ValueError("Invalid graphics API")
        games.set_api_override(entry.game.folder, api or None)
        return self.select_executable(entry, entry.game.exe)

    def install(self, entry, options, emit):
        return installer.install(entry.game, options,
                                 on_step=lambda i, n, text: emit("log", f"[{i+1}/{n}] {text}"),
                                 on_log=lambda text: emit("log", text),
                                 on_prog=lambda p, text: emit("progress", (p, text)))

    def uninstall(self, entry, emit):
        return installer.uninstall(entry.game, on_log=lambda text: emit("log", text))

    def preview(self, entry, options):
        return "\n".join(installer.preview_lines(installer.preview(entry.game, options)))

    def diagnose(self, entry):
        report = diagnose.analyse(entry.game.install_dir)
        return report.verdict + "\n\n" + "\n\n".join(
            f"[{item.level}] {item.title}\n{item.detail}" for item in report.findings)

    def versions(self, entry):
        return "\n".join(f"{item.name}\n  {item.installed or '—'} → {item.latest or '—'}"
                         for item in components.check(entry.game.install_dir))

    def catalog(self):
        return sources.rhi_catalog(), sources.feeder_releases()

    def update_all(self, entries, emit):
        count = 0
        for entry in entries:
            if not entry.installed:
                continue
            options = installer.options_from_manifest(entry.game.install_dir)
            if options is None:
                continue
            emit("log", entry.game.name)
            self.install(entry, options, emit)
            count += 1
        return count
