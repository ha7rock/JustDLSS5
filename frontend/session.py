"""Session diagnostics and explicit tuning actions, executed by desktop workers."""
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .backend import autotune, diagnose, dlss, feedcfg, installer, optiscaler, wincrash


@dataclass
class SessionResult:
    text: str
    folder: str
    route: str
    resolution: int = 0
    measured: int = 0
    verdict: str = ""
    findings: list = field(default_factory=list)
    log_time: str = ""
    crash: object = None
    related_crash: bool = False
    target: int = 0


def work_applies(game, route):
    return route == dlss.OPTI or (route == dlss.FEEDER and game.api == "DX11" and game.bitness == 64)


def current_crash(crash, folder):
    if crash is None:
        return False
    paths = [folder / diagnose.FEED_LOG, folder / "ReShade.log", folder / "host64/dlss5-feed-host.log",
             folder / "dlss5-bridge.log", folder / "rtx-remix/logs/remix-dxvk.log"]
    opti = diagnose._opti_log(folder)
    if opti:
        paths.append(opti)
    stamps = []
    for path in paths:
        try:
            stamps.append(path.stat().st_mtime)
        except OSError:
            pass
    try:
        stamp = datetime.strptime(crash.when[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        return False
    return not stamps or stamp >= max(stamps) - 300


def analyse(entry, target=0):
    game, folder = entry.game, entry.game.install_dir
    report = diagnose.analyse(folder)
    manifest = diagnose._manifest(folder) or {}
    route = str(manifest.get("path") or "")
    crash = wincrash.last_crash(game.exe.name, since=diagnose._installed_at(folder) or 0) if game.exe else None
    related = current_crash(crash, folder)
    verdict = report.verdict
    if related and verdict.startswith("Working"):
        verdict = "模型曾运行，但 Windows 记录了游戏崩溃。 / The model ran, but Windows recorded a game crash."
    lines = [verdict, *[f"[{item.level}] {item.title}\n{item.detail}" for item in report.findings]]
    if crash:
        description = wincrash.describe(crash, str(manifest.get("proxy") or ""), tuple(manifest.get("files") or []))
        if description:
            prefix = "" if related else "较早的崩溃记录 / Earlier crash record:\n"
            lines.append(prefix + "\n".join(description))
    result = SessionResult("", str(folder), route, verdict=verdict,
                           findings=list(report.findings), log_time=getattr(report, "log_time", ""),
                           crash=crash, related_crash=related, target=target)
    if target and report.ran and not related and work_applies(game, route):
        resolution = autotune.ran_at(folder, route, 100)
        feed = diagnose._last_run(diagnose._tail(folder / diagnose.FEED_LOG, 100_000))
        opti_path = diagnose._opti_log(folder)
        opti = diagnose._last_run(diagnose._tail(opti_path, 100_000)) if opti_path else ""
        measured = autotune.measure(feed, opti, route, resolution)
        if measured:
            autotune.remember(folder, measured)
            rows = [row for row in autotune.history(folder) if row.get("route") == route]
            suggestion = autotune.suggest(rows, target, measured.resolution, route, measured)
            if suggestion:
                lines.extend(suggestion.lines)
                result.measured = measured.resolution
                minimum = optiscaler.NR_SCALE_MIN if route == dlss.OPTI else 50
                recommended = max(minimum, min(100, suggestion.resolution))
                if recommended != suggestion.resolution:
                    lines.append(f"当前路线最低 {minimum}%。 / This route supports a minimum of {minimum}%.")
                if recommended != measured.resolution:
                    result.resolution = recommended
        else:
            lines.append("日志中没有足够的性能数据。 / No usable performance measurements in the logs.")
    result.text = "\n\n".join(lines)
    return result


def apply(entry, result):
    folder = entry.game.install_dir
    options = installer.options_from_manifest(folder)
    if (str(folder) != result.folder or options is None or options.path != result.route
            or not work_applies(entry.game, result.route)):
        raise ValueError("安装配置已变化，请重新诊断。 / Installation changed; diagnose again.")
    minimum = optiscaler.NR_SCALE_MIN if result.route == dlss.OPTI else 50
    if not minimum <= result.resolution <= 100:
        raise ValueError("Invalid suggested resolution")
    if autotune.ran_at(folder, result.route, 100) != result.measured:
        raise ValueError("渲染设置已变化，请重新诊断。 / Work area changed; diagnose again.")
    config = folder / ("OptiScaler.ini" if result.route == dlss.OPTI else "dlss5-feed.cfg")
    if not config.is_file():
        raise ValueError("配置文件不存在，请重新安装组件。 / Configuration missing; reinstall components.")
    if result.route == dlss.OPTI:
        optiscaler.enable_nr(folder, settings={"WorkingScale": result.resolution / 100})
    else:
        feedcfg.write(folder, {"work_resolution": result.resolution})
    if autotune.ran_at(folder, result.route, -1) != result.resolution:
        raise OSError("配置未写入，请检查权限或游戏占用。 / Setting was not saved; check permissions or close the game.")
    return result.resolution
