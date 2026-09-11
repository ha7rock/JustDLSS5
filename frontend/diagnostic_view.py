"""Read-only, localized diagnostic presentation shared by both entry points."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout, QLabel,
                              QPlainTextEdit, QScrollArea, QSizePolicy, QTabWidget,
                              QVBoxLayout, QWidget)

from .controls import Button
from .diagnostic_text import NEXT_STEPS, translate


def _label(text, kind=""):
    widget = QLabel(text)
    widget.setObjectName(kind)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    widget.setWordWrap(True)
    widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    return widget


class DiagnosticDialog(QDialog):
    def __init__(self, result, game_name, chinese=True, parent=None):
        super().__init__(parent)
        self.chinese = chinese
        self.setWindowTitle(self.t("运行检查", "Session check"))
        self.resize(720, 580)
        screen = self.screen().availableGeometry()
        self.resize(min(self.width(), screen.width() - 40), min(self.height(), screen.height() - 60))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.addWidget(_label(game_name, "subheading"))
        context = self.t("安装文件与最近一次运行记录", "Installation files and latest session records")
        if result.log_time:
            context += self.t("\n日志时间：", "\nLog time: ") + result.log_time
        layout.addWidget(_label(context, "muted"))
        self.tabs = QTabWidget()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        content = QWidget()
        body = QVBoxLayout(content)
        body.setContentsMargins(0, 12, 8, 12)
        body.setSpacing(12)
        self.scroll.setWidget(content)
        self.tabs.addTab(self.scroll, self.t("检查结果", "Results"))
        self.raw = QPlainTextEdit()
        self.raw.setReadOnly(True)
        self.raw.setPlainText(result.text)
        self.tabs.addTab(self.raw, self.t("原始记录", "Original report"))
        layout.addWidget(self.tabs, 1)

        if result.related_crash:
            verdict = self.t("Windows 记录了近期游戏崩溃。即使模型曾运行，也需要排查。",
                             "Windows recorded a recent game crash. Model activity alone does not confirm a healthy session.")
        else:
            verdict = translate(result.verdict, chinese)
        body.addWidget(_label(self.t("结论", "Conclusion"), "subheading"))
        body.addWidget(_label(verdict or self.t("暂时无法生成中文结论，以下为上游原文。",
                                               "No conclusion is available."), "notice"))
        if not verdict:
            body.addWidget(_label(result.verdict or result.text))

        if result.crash:
            crash = result.crash
            heading = self.t("近期崩溃记录", "Recent crash record") if result.related_crash else self.t("较早的崩溃记录", "Earlier crash record")
            frame, box = self.card(heading)
            box.addWidget(_label(self.t("时间（UTC）：", "Time (UTC): ") + str(crash.when)))
            box.addWidget(_label(self.t("程序：", "Program: ") + str(crash.exe)))
            box.addWidget(_label(self.t("出错模块：", "Faulting module: ") + str(crash.module)))
            box.addWidget(_label(self.t("错误码：", "Error code: ") + str(crash.code)))
            box.addWidget(_label(self.t("时间关联不能确定崩溃原因；详细堆栈见原始记录。" if result.related_crash else
                                        "早于当前运行记录，不用于判断本次运行是否成功。",
                                        "Timing alone does not establish the cause; see the original report." if result.related_crash else
                                        "Predates the current session and is not used to judge its outcome."), "muted"))
            body.addWidget(frame)

        # Keep upstream order within each group and never hide unfamiliar levels.
        issues = [f for f in result.findings if f.level in ("bad", "warn")]
        notes = [f for f in result.findings if f.level not in ("bad", "warn", "ok")]
        passed = [f for f in result.findings if f.level == "ok"]
        self.groups = {}
        for key, title, rows in (("issues", self.t("需要关注", "Needs attention"), issues),
                                 ("notes", self.t("运行信息", "Session information"), notes),
                                 ("passed", self.t("已通过", "Passed checks"), passed)):
            if not rows:
                continue
            group = QWidget()
            group_layout = QVBoxLayout(group)
            group_layout.setContentsMargins(0, 0, 0, 0)
            for finding in rows:
                group_layout.addWidget(self.finding(finding))
            self.groups[key] = group
            if key == "passed":
                toggle = Button(f"{title} ({len(rows)}) ▸")
                toggle.setCheckable(True)
                toggle.toggled.connect(group.setVisible)
                toggle.toggled.connect(lambda on, b=toggle, name=title, n=len(rows):
                                       b.setText(f"{name} ({n}) {'▾' if on else '▸'}"))
                body.addWidget(toggle)
                group.hide()
            else:
                body.addWidget(_label(f"{title} ({len(rows)})", "subheading"))
            body.addWidget(group)

        if result.target:
            frame, box = self.card(self.t("渲染比例建议", "Render scale suggestion"))
            box.addWidget(_label(self.t(f"目标帧率：{result.target} FPS", f"Target: {result.target} FPS")))
            if result.resolution:
                box.addWidget(_label(self.t(f"建议从 {result.measured}% 调整为 {result.resolution}%。降低比例可能减少细节。",
                                            f"Suggested change: {result.measured}% → {result.resolution}%. Lower scales may reduce detail.")))
                box.addWidget(_label(self.t("点击下方按钮才会保存，下次启动游戏生效。估算依据见原始记录。",
                                            "Only the button below saves this change, for the next launch. See the original report for measurements."), "muted"))
            else:
                box.addWidget(_label(self.t("本次没有可应用的调整。可能无需改变比例、数据不足，或当前路线不支持；详情见原始记录。",
                                            "No applicable change from this check. The scale may already fit, data may be insufficient, or the route may be unsupported; see the original report.")))
            body.addWidget(frame)
        body.addStretch()
        footer = QHBoxLayout()
        copy = Button(self.t("复制原始记录", "Copy original report"))
        def copy_report():
            QApplication.clipboard().setText(result.text)
            copy.setText(self.t("已复制", "Copied"))
        copy.clicked.connect(copy_report)
        footer.addWidget(copy)
        footer.addStretch()
        close = Button(self.t("关闭", "Close"))
        close.clicked.connect(self.reject)
        footer.addWidget(close)
        layout.addLayout(footer)
        if result.resolution:
            apply = Button(self.t(f"应用 {result.resolution}%（下次启动生效）",
                                  f"Apply {result.resolution}% (next launch)"))
            apply.setObjectName("primary")
            apply.setAutoDefault(False)
            apply.clicked.connect(self.accept)
            layout.addWidget(apply)

    def t(self, zh, en):
        return zh if self.chinese else en

    def card(self, title):
        frame = QFrame()
        frame.setObjectName("card")
        box = QVBoxLayout(frame)
        box.setContentsMargins(14, 12, 14, 12)
        box.addWidget(_label(title))
        return frame, box

    def finding(self, finding):
        levels = {"bad": self.t("异常", "Error"), "warn": self.t("注意", "Warning"),
                  "info": self.t("提示", "Info"), "check": self.t("检查", "Check"),
                  "ok": self.t("通过", "Passed")}
        title = translate(finding.title, self.chinese)
        frame, box = self.card(f"{levels.get(finding.level, finding.level)} · " + (title or finding.title))
        heading = box.itemAt(0).widget()
        heading.setObjectName({"bad": "warning", "warn": "notice", "ok": "badge"}.get(finding.level, ""))
        if self.chinese and title is None:
            box.addWidget(_label("此条为上游新增或未适配的提示，保留原文。", "muted"))
        if finding.title in NEXT_STEPS:
            box.addWidget(_label(self.t(*NEXT_STEPS[finding.title])))
        if finding.detail:
            detail = translate(finding.detail, self.chinese)
            if detail is not None:
                box.addWidget(_label(detail, "muted"))
            else:
                toggle = Button(self.t("查看详细说明（上游原文） ▸", "Show details ▸"))
                toggle.setCheckable(True)
                source = _label(finding.detail, "muted")
                toggle.toggled.connect(source.setVisible)
                toggle.toggled.connect(lambda on: toggle.setText(self.t(
                    "收起详细说明 ▾" if on else "查看详细说明（上游原文） ▸",
                    "Hide details ▾" if on else "Show details ▸")))
                box.addWidget(toggle)
                box.addWidget(source)
                source.hide()
        return frame
