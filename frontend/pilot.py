"""Explicit, cancellable desktop entry point for upstream route trials."""
from dataclasses import replace
from threading import Event

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QProgressBar
from PySide6.QtCore import Qt
from .backend import anticheat, autopilot, dlss, installer
from .controls import Button
from .jobs import Jobs


def prepare(entry, options, inspection):
    game = entry.game
    if not installer.check_supported(game)[0]:
        raise ValueError("请先完成程序识别。 / Complete game detection first.")
    # Refuse uncertain detection instead of letting an exception permit launch.
    if anticheat.detect(game.install_dir, game.folder).present:
        raise ValueError("检测到反作弊，不提供自动尝试。 / Anti-cheat detected; automatic trials are unavailable.")
    if options.vr:
        raise ValueError("OpenXR 请使用手动安装。 / Use manual installation for OpenXR.")
    offered = [r for r in inspection.support.options if inspection.fit.get(r, (False, ""))[0]]
    if options.path not in offered:
        raise ValueError("当前路线不可用。 / The selected route is unavailable.")
    routes = autopilot.plan(options.path, offered)
    choices = {}
    for route in routes:
        choices[route] = replace(options, path=route,
            fg=options.fg and route == dlss.OPTI and game.api == "DX12",
            mfg=options.mfg and inspection.mfg_available and route not in (dlss.OPTI, dlss.REMIX),
            vr=False, remix_swap=options.remix_swap and route == dlss.REMIX,
            renodx=options.renodx if (route == dlss.RENODX) == (options.path == dlss.RENODX) else None,
            renodx_local=options.renodx_local if (route == dlss.RENODX) == (options.path == dlss.RENODX) else None)
    return routes, choices, autopilot.may_start(game)


def run(entry, plan, stop, emit):
    routes, choices, _ = plan
    game = entry.game
    def check():
        if stop.is_set():
            raise RuntimeError("已停止 / Stopped")
        if anticheat.detect(game.install_dir, game.folder).present:
            stop.set()
            raise RuntimeError("检测到反作弊，停止自动尝试。 / Anti-cheat detected; trials stopped.")
    def install(g, opt):
        check()
        emit("log", "正在安装 / Installing: " + opt.path)
        return installer.install(g, opt, on_log=lambda text: emit("log", text))
    def start(g):
        if stop.is_set():
            return False, "Stopped before launch"
        check()
        emit("log", "等待游戏启动与加载记录；如未启动，请从游戏平台打开。 / Waiting for the game; launch it through its store if needed.")
        return autopilot.start(g)
    hooks = autopilot.Hooks(install=install, start=start, stop=stop.is_set,
        options=lambda base, route: choices[route], log=lambda text, kind="": emit("log", text))
    return autopilot.run(game, choices[routes[0]], routes, hooks)


class PilotDialog(QDialog):
    def __init__(self, entry, plan, chinese, parent=None):
        super().__init__(parent)
        self.chinese, self.entry, self.plan = chinese, entry, plan
        self.stop = Event()
        self.started = False
        self.jobs = Jobs(self)
        self.jobs.events.connect(self._events)
        self.jobs.completed.connect(self._done)
        self.setWindowTitle(self.t("自动尝试路线（实验性）", "Automatic route trials (experimental)"))
        self.resize(650, 550)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        self.status = QLabel(entry.game.name)
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.status)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlainText(self.t(
            "将安装并尝试启动游戏，读取已加载的 DLL。未加载成功时，会等待你关闭游戏，再安装下一条路线，不会再次询问。最多尝试三条路线。\n\n停止会等待当前安装结束，不会强制关闭游戏，也不会自动卸载已安装的组件。加载成功仅表示组件接入，不代表画质或稳定性验证通过。\n\n路线顺序：",
            "Installs and attempts to launch the game, then reads loaded DLLs. If loading fails, waits for you to close the game and installs the next route without asking again. Up to three routes.\n\nStop waits for the current installation to finish. It neither kills the game nor uninstalls components. Loading confirms attachment, not visual quality or stability.\n\nRoute order: ") + " → ".join(plan[0]) +
            ("\n\n" + plan[2][1] if plan[2][1] else ""))
        layout.addWidget(self.log, 1)
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)
        row = QHBoxLayout()
        self.start_button = Button(self.t("确认并开始", "Confirm and start"))
        self.start_button.clicked.connect(self._start)
        row.addWidget(self.start_button)
        self.close_button = Button(self.t("取消", "Cancel"))
        self.close_button.clicked.connect(self.reject)
        row.addWidget(self.close_button)
        layout.addLayout(row)

    def t(self, zh, en):
        return zh if self.chinese else en

    def _start(self):
        if self.started:
            return
        self.started = True
        self.start_button.setEnabled(False)
        self.start_button.set_loading(True)
        self.close_button.setText(self.t("停止", "Stop"))
        self.progress.setRange(0, 0)
        self.progress.show()
        self.status.setText(self.t("正在自动尝试；详细进度见下方。", "Trying routes; see progress below."))
        self.jobs.submit(lambda emit: run(self.entry, self.plan, self.stop, emit))

    def _events(self, events):
        for _, kind, text in events:
            self.log.appendPlainText(str(text))

    def _done(self, job, result, error):
        self.start_button.set_loading(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        if error:
            self.status.setText(self.t("操作失败，请检查下方记录及当前安装状态。", "Failed; check the log and current installation state."))
            self.log.appendPlainText(error[0])
        else:
            self.status.setText(self.t("组件已加载；请继续游玩并检查运行记录。", "Components loaded; play and check the session report.") if result.ok else self.t("尝试已结束，未确认组件成功加载。", "Trials ended without confirming component loading."))
            self.log.appendPlainText(self.t("当前目录记录的路线：", "Route recorded in the folder: ") + (result.left or "—"))
            self.log.appendPlainText(autopilot.summary(result))
        self.close_button.setEnabled(True)
        self.close_button.setText(self.t("关闭", "Close"))

    def reject(self):
        if self.jobs.active:
            self.stop.set()
            self.close_button.setEnabled(False)
            self.status.setText(self.t("正在停止；等待当前安装安全结束。", "Stopping after the current installation finishes."))
            return
        self.jobs.shutdown()
        super().reject()

    def closeEvent(self, event):
        if self.jobs.active:
            self.reject()
            event.ignore()
        else:
            self.jobs.shutdown()
            event.accept()
