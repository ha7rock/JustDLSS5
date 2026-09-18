"""Explicit, asynchronous maintenance of upstream-owned files and registrations."""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QProgressBar)
from .backend import dlssupdate, installer, openxr, remixdl
from .controls import Button
from .jobs import Jobs


def remove_remix(game, emit):
    installer.preflight(game)
    return remixdl.remove(game.install_dir, log=lambda text: emit('log', text))


class MaintenanceDialog(QDialog):
    def __init__(self, chinese, parent=None):
        super().__init__(parent)
        self.chinese = chinese
        self.jobs = Jobs(self)
        self.jobs.completed.connect(self.completed)
        self.jobs.events.connect(self.events)
        self.callback = None
        self.actions = []
        self.resize(760, 560)
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(24, 24, 24, 24)
        self.body.setSpacing(14)
        self.status = QLabel()
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.status.setWordWrap(True)
        self.body.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.hide()
        self.body.addWidget(self.progress)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.body.addWidget(self.log, 1)
        self.buttons = QHBoxLayout()
        self.body.addLayout(self.buttons)
        self.close_button = Button(self.t('关闭', 'Close'))
        self.close_button.clicked.connect(self.reject)
        self.buttons.addWidget(self.close_button)

    def t(self, zh, en):
        return zh if self.chinese else en

    def action(self, title, callback):
        widget = Button(title)
        widget.clicked.connect(callback)
        self.actions.append(widget)
        self.buttons.insertWidget(len(self.actions) - 1, widget)
        return widget

    def submit(self, work, done, title):
        if self.jobs.active:
            return
        self.callback = done
        self.status.setText(title)
        self.progress.setRange(0, 0)
        self.progress.show()
        for widget in self.actions:
            widget.setEnabled(False)
        self.close_button.setEnabled(False)
        self.jobs.submit(work)

    def events(self, events):
        for _, kind, value in events:
            if kind == 'log':
                self.log.appendPlainText(str(value))
            elif kind == 'progress':
                done, total = value
                if total:
                    self.progress.setRange(0, 100)
                    self.progress.setValue(min(100, int(done * 100 / total)))

    def completed(self, job, result, error):
        self.progress.hide()
        self.close_button.setEnabled(True)
        for widget in self.actions:
            widget.setEnabled(True)
        callback, self.callback = self.callback, None
        if error:
            self.status.setText(self.t('操作失败，详细原因见下方。', 'Failed. See the details below.'))
            self.log.appendPlainText(error[0])
        elif callback:
            callback(result)

    def reject(self):
        if self.jobs.active:
            self.status.setText(self.t('正在处理，完成后可关闭。', 'Please wait for the operation to finish.'))
            return
        self.jobs.shutdown()
        super().reject()

    def closeEvent(self, event):
        if self.jobs.active:
            event.ignore()
        else:
            self.jobs.shutdown()
            event.accept()


class RuntimeDialog(MaintenanceDialog):
    def __init__(self, game, chinese, parent=None):
        super().__init__(chinese, parent)
        self.game = game
        self.setWindowTitle(self.t('DLSS 文件 — ', 'DLSS files — ') + game.name)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([self.t('文件', 'File'), self.t('当前', 'Current'),
            self.t('可用', 'Available'), self.t('状态', 'Status')])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.body.insertWidget(1, self.table, 2)
        self.log.setPlainText(self.t(
            '更新游戏原生 DLSS 的超分辨率（SR）、帧生成（FG）和光线重建（RR）文件。它们不是 DLSS 5 神经渲染组件。\n原始文件会备份，可在此还原；由 DLSS 5 安装器管理的文件会跳过。反作弊游戏不提供更新。',
            'Updates native DLSS super resolution (SR), frame generation (FG), and ray reconstruction (RR). These are not DLSS 5 neural rendering components.\nOriginal files are backed up for restoration here. Files managed by the DLSS 5 installer are skipped. Updates are refused for anti-cheat games.'))
        self.action(self.t('重新检查', 'Refresh'), self.refresh)
        self.action(self.t('更新 DLSS 文件', 'Update DLSS files'), lambda: self.change(False))
        self.action(self.t('还原原始文件', 'Restore originals'), lambda: self.change(True))
        QTimer.singleShot(0, self.refresh)

    def refresh(self):
        def work(emit):
            entries = dlssupdate.scan(self.game, fresh=True)
            try:
                latest = dlssupdate.newest(refresh=True)
                error = '' if latest else '无法获取版本列表 / Could not retrieve available builds.'
            except Exception as exc:
                latest, error = {}, str(exc)
            return entries, latest, error
        self.submit(work, self.scanned, self.t('正在检查文件和可用版本…', 'Checking files and available builds…'))

    def scanned(self, result):
        entries, latest, error = result
        self.table.setRowCount(len(entries))
        states = {'original': self.t('游戏原始文件', 'Original'), 'updated': self.t('已更新，可还原', 'Updated; can restore'),
            'install': self.t('由 DLSS 5 安装器管理', 'Managed by DLSS 5'), 'missing': self.t('文件缺失', 'Missing')}
        for row, entry in enumerate(entries):
            values = (entry.rel, entry.version or '—', (latest.get(entry.family) or {}).get('label', '—'), states.get(entry.state, entry.state))
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setToolTip(str(value))
                self.table.setItem(row, col, item)
        self.table.resizeRowsToContents()
        self.status.setText(self.t('检查完成。', 'Check complete.') if entries else self.t('未找到原生 DLSS 文件；仍可尝试还原已有备份。', 'No native DLSS files found. Existing backups can still be restored.'))
        if error:
            self.log.appendPlainText(error)

    def change(self, restore):
        if self.jobs.active:
            return
        title = self.t('还原原始文件', 'Restore originals') if restore else self.t('更新 DLSS 文件', 'Update DLSS files')
        text = self.game.name + '\n' + str(self.game.folder) + '\n\n' + self.t(
            '请先关闭游戏。还原本工具保存的原始文件？' if restore else '请先关闭游戏。下载并替换此游戏需要更新的 DLSS 文件？原始文件会先备份。',
            'Close the game first. Restore the original files backed up by this tool?' if restore else 'Close the game first. Download and replace outdated DLSS files for this game? Originals will be backed up first.')
        if QMessageBox.question(self, title, text) != QMessageBox.StandardButton.Yes:
            return
        def work(emit):
            return dlssupdate.restore(self.game) if restore else dlssupdate.update(self.game,
                progress=lambda done, total: emit('progress', (done, total)))
        self.submit(work, self.changed, self.t('正在处理…', 'Working…'))

    def changed(self, report):
        self.status.setText(self.t('操作完成。', 'Operation complete.') if report.ok else self.t('未完成，请查看结果。', 'Not completed. See the results.'))
        for title, values in ((self.t('已处理', 'Changed'), report.done), (self.t('跳过', 'Skipped'), report.skipped),
                              (self.t('说明', 'Notes'), report.notes)):
            if values:
                self.log.appendPlainText(title + ':\n' + '\n'.join(values))
        if report.error or report.refused:
            self.log.appendPlainText(report.error or report.refused)
        if not any((report.done, report.skipped, report.notes, report.error, report.refused)):
            self.log.appendPlainText(self.t('没有需要处理的文件。', 'No files needed changes.'))
        # Keep the outcome visible; refreshing is explicit and never overwrites it.


class OpenXRDialog(MaintenanceDialog):
    def __init__(self, chinese, parent=None):
        super().__init__(chinese, parent)
        self.setWindowTitle(self.t('OpenXR 注册管理', 'OpenXR registration'))
        self.log.setPlainText(self.t(
            'OpenXR 层会作用于当前用户的所有 OpenXR 应用，不只当前游戏。VR 支持仍为实验性，尚未经过头显实测。\n移除注册后停止全局加载，不删除游戏文件，也不会移除其他工具的注册。',
            'The OpenXR layer affects all OpenXR applications for this user. VR support is experimental and has not been verified on a headset.\nRemoving registration stops global loading; it does not delete game files or remove another tool’s registration.'))
        self.action(self.t('重新检查', 'Refresh'), self.refresh)
        self.remove_button = self.action(self.t('移除本工具的注册', 'Remove this tool’s registration'), self.remove)
        self.remove_button.setEnabled(False)
        QTimer.singleShot(0, self.refresh)

    def refresh(self):
        self.submit(lambda emit: openxr.registrations(), self.scanned, self.t('正在检查注册…', 'Checking registrations…'))

    def scanned(self, registrations):
        ours = any(openxr.is_ours(path) for path, value in registrations)
        self.remove_button.setEnabled(ours)
        self.status.setText(self.t('检测到本工具的注册。', 'This tool has a registration.') if ours else self.t('未检测到本工具的注册。', 'No registration from this tool.'))
        for path, value in registrations:
            self.log.appendPlainText(str(path) + (' [启用 / Active]' if value == 0 else ' [停用 / Disabled]'))

    def remove(self):
        if self.jobs.active:
            return
        if QMessageBox.question(self, self.windowTitle(), self.t('请先关闭 VR 游戏。移除当前用户下本工具的 OpenXR 注册？',
                'Close VR games first. Remove this tool’s OpenXR registration for the current user?')) != QMessageBox.StandardButton.Yes:
            return
        def done(removed):
            self.status.setText(self.t('注册已移除。', 'Registration removed.') if removed else self.t('未移除注册，请重新检查。', 'No registration removed. Refresh to check.'))
            self.remove_button.setEnabled(False)
        self.submit(lambda emit: openxr.unregister(), done, self.t('正在移除注册…', 'Removing registration…'))