"""Library-first native Qt workspace. No dependency on the legacy Tk interface."""
from dataclasses import replace
from pathlib import Path
import sys
import time

from PySide6.QtCore import Qt, QTimer, QUrl, QSize
from PySide6.QtGui import QDesktopServices, QFont, QIcon, QPixmap, QPainter, QColor, QPen, QKeySequence, QShortcut
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QLineEdit, QComboBox, QTableView,
    QHeaderView, QAbstractItemView, QSplitter, QScrollArea, QFormLayout, QSlider,
    QCheckBox, QToolButton, QPlainTextEdit, QProgressBar, QFileDialog, QMessageBox,
    QDialog, QMenu, QInputDialog, QSizePolicy, QStyle)

from .backend import prefs, update, dlss, installer, feedcfg, reshade_ini, optiscaler, profiles, video, compare, remixlist, remixdl
from .service import BackendService, LibraryEntry
from .jobs import Jobs
from .library import LibraryModel, LibraryFilter, LibraryTable
from .theme import STYLES
from .controls import Button, ComboBox, Slider
from .about import NAME, VERSION, REPOSITORY
from . import feedback, updates


def column(parent=None, margins=0, spacing=12):
    layout = QVBoxLayout(parent)
    layout.setContentsMargins(margins, margins, margins, margins)
    layout.setSpacing(spacing)
    return layout


def row(parent=None, spacing=10):
    layout = QHBoxLayout(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(spacing)
    return layout


def label(text="", kind="", wrap=False):
    widget = QLabel(text)
    widget.setObjectName(kind)
    widget.setWordWrap(wrap)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    return widget


def button(text, callback, kind=""):
    widget = Button(text)
    widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    widget.setToolTip(text)
    widget.setObjectName(kind)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    widget.clicked.connect(callback)
    return widget


def scroller(content):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(content)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    return scroll


def navigation_icon(kind):
    pixmap = QPixmap(40, 40)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(2, 2)
    painter.setPen(QPen(QColor("#aebbc9"), 1.5))
    if kind == "library":
        for x in (3, 11):
            for y in (3, 11):
                painter.drawRoundedRect(x, y, 6, 6, 1, 1)
    elif kind == "video":
        painter.drawRoundedRect(2, 3, 16, 14, 2, 2)
        painter.drawLine(8, 7, 13, 10)
        painter.drawLine(13, 10, 8, 13)
        painter.drawLine(8, 13, 8, 7)
    elif kind == "activity":
        for y in (5, 10, 15):
            painter.drawLine(7, y, 17, y)
            painter.drawPoint(3, y)
    elif kind == "settings":
        for x, y in ((4, 6), (10, 13), (16, 8)):
            painter.drawLine(x, 3, x, 17)
            painter.drawEllipse(x-2, y-2, 4, 4)
    elif kind == "remix":
        painter.drawRect(3, 3, 10, 10)
        painter.drawRect(7, 7, 10, 10)
    else:
        painter.drawRoundedRect(4, 2, 12, 16, 2, 2)
        for y in (7, 11, 14):
            painter.drawLine(7, y, 13, y)
    painter.end()
    return QIcon(pixmap)


class EmptyArtwork(QWidget):
    """Small resolution-independent illustration, not a downloaded game cover."""
    def __init__(self):
        super().__init__()
        self.setFixedSize(160, 116)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor("#424c59"), 1.5))
        p.setBrush(QColor("#191e25"))
        p.drawRoundedRect(20, 18, 118, 73, 10, 10)
        p.setPen(QPen(QColor("#b6e477"), 2))
        p.drawLine(54, 51, 70, 51)
        p.drawLine(62, 43, 62, 59)
        p.drawEllipse(96, 44, 5, 5)
        p.drawEllipse(105, 55, 5, 5)
        p.setPen(QPen(QColor("#424c59"), 2))
        p.drawLine(69, 92, 69, 103)
        p.drawLine(88, 92, 88, 103)
        p.drawLine(56, 104, 103, 104)
        p.end()


class MainWindow(QMainWindow):
    def __init__(self, service=None, background=True):
        super().__init__()
        self.service = service or BackendService()
        self.chinese = prefs.get("language", "zh_CN") == "zh_CN"
        self.model = LibraryModel(self)
        self.proxy = LibraryFilter(self)
        self.proxy.setSourceModel(self.model)
        self.current = None
        self.inspection = None
        self.options = installer.Options()
        self.jobs = Jobs(self)
        self.jobs.completed.connect(self._completed)
        self.jobs.events.connect(self._events)
        self.callbacks = {}
        self.update_check_running = False
        self.busy_job = None
        self.scan_job = None
        self.selection_generation = 0
        self.log_lines = []
        self.catalog_loaded = False
        self.catalog = {}
        self.addon_family = None
        self._detail_ready = False
        self.setWindowTitle(NAME)
        self.setMinimumSize(900, 620)
        screen = QApplication.primaryScreen().availableGeometry()
        default_size = [min(1440, screen.width() - 80), min(900, screen.height() - 80)]
        # Apply the revised default once, then remember subsequent user resizing.
        size = prefs.get("studio_window", default_size) if prefs.get("studio_window_layout", 0) >= 1 else default_size
        if not isinstance(size, list) or len(size) != 2 or not all(isinstance(x, int) for x in size):
            size = default_size
        self.resize(min(max(900, size[0]), screen.width()), min(max(620, size[1]), screen.height()))
        self.move(screen.x() + (screen.width() - self.width()) // 2,
                  screen.y() + max(30, (screen.height() - self.height()) // 2))
        self.setStyleSheet(STYLES)
        self.app_icon = QIcon(str(Path(__file__).with_name("justdlss5.ico")))
        self.setWindowIcon(self.app_icon)
        self._build()
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self.focus_search)
        if background:
            self._submit(lambda emit: self.service.hardware(), self._hardware)
            if prefs.get("product_update_check", True) and updates.check_due(prefs.get("product_update_checked", 0), time.time()):
                self.check_product_update(automatic=True)

    def t(self, zh, en):
        return zh if self.chinese else en

    def _build(self):
        self.model.chinese = self.chinese
        shell = QWidget()
        layout = row(shell, 0)
        side = QWidget()
        side.setObjectName("sidebar")
        side.setFixedWidth(184)
        nav = column(side, 18, 8)
        brand = row(spacing=10)
        monogram = label()
        monogram.setPixmap(self.app_icon.pixmap(QSize(32, 32)))
        monogram.setFixedSize(32, 32)
        monogram.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.addWidget(monogram)
        brand.addWidget(label(NAME, "subheading"))
        nav.addLayout(brand)
        nav.addWidget(label(self.t("游戏画面组件管理", "GAME GRAPHICS TOOLS"), "eyebrow"))
        nav.addSpacing(32)
        nav.addWidget(label(self.t("工作空间", "WORKSPACE"), "eyebrow"))
        self.nav_buttons = []
        for i, title in enumerate((self.t("游戏库", "Game library"), self.t("视频增强", "Video studio"),
                                   self.t("任务与日志", "Activity"), self.t("设置", "Settings"))):
            btn = button(title, lambda checked=False, n=i: self.navigate(n), "nav")
            btn.setIcon(navigation_icon(("library", "video", "activity", "settings")[i]))
            btn.setCheckable(True)
            nav.addWidget(btn)
            self.nav_buttons.append(btn)
        nav.addStretch()
        nav.addWidget(label(self.t("工具与帮助", "TOOLS & HELP"), "eyebrow"))
        remix_button = button("RTX Remix ↗", self.show_remix, "nav")
        remix_button.setIcon(navigation_icon("remix"))
        nav.addWidget(remix_button)
        docs_button = button(self.t("项目文档 ↗", "Documentation ↗"),
                             lambda: QDesktopServices.openUrl(QUrl(REPOSITORY)), "nav")
        docs_button.setIcon(navigation_icon("docs"))
        nav.addWidget(docs_button)
        feedback_button = button(self.t("反馈问题 ↗", "Report a problem ↗"), self.report_problem, "nav")
        feedback_button.setIcon(navigation_icon("docs"))
        nav.addWidget(feedback_button)
        nav.addSpacing(14)
        self.language = ComboBox()
        self.language.addItems(["简体中文", "English"])
        self.language.setCurrentIndex(0 if self.chinese else 1)
        self.language.currentIndexChanged.connect(self.change_language)
        nav.addWidget(self.language)
        nav.addWidget(label(f"v{VERSION}  ·  Core {update.VERSION}", "muted"))
        layout.addWidget(side)
        right = QWidget()
        body = column(right, 0, 0)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._library_page())
        self.pages.addWidget(self._video_page())
        self.pages.addWidget(self._activity_page())
        self.pages.addWidget(self._settings_page())
        body.addWidget(self.pages, 1)
        footer = QWidget()
        footer_layout = row(footer)
        footer_layout.setContentsMargins(26, 12, 26, 12)
        self.status = label(self.t("●  就绪", "●  Ready"), "muted")
        self.status.setMinimumWidth(0)
        footer_layout.addWidget(self.status, 1)
        self.gpu_label = label("", "muted")
        footer_layout.addWidget(self.gpu_label)
        body.addWidget(footer)
        layout.addWidget(right, 1)
        self.setCentralWidget(shell)
        self.navigate(0)
        self._filter()

    def _page_header(self, layout, title, subtitle):
        header = row()
        text = column(spacing=5)
        text.addWidget(label(title, "heading"))
        text.addWidget(label(subtitle, "muted", True))
        header.addLayout(text, 1)
        layout.addLayout(header)
        return header

    def _library_page(self):
        page = QWidget()
        layout = column(page, 26, 20)
        header = self._page_header(layout, self.t("游戏库", "Game library"),
            self.t("扫描游戏，安装或卸载 DLSS 5 组件。", "Scan games and install or remove DLSS 5 components."))
        self.add_button = button(self.t("＋ 添加游戏", "+ Add game"), self.add_game)
        self.scan_button = button(self.t("扫描游戏", "Scan library"), self.scan, "primary")
        scan_labels = (self.scan_button.text(), self.t("扫描中…", "Scanning…"), self.t("重新扫描", "Rescan"))
        self.scan_button.setMinimumWidth(max(self.scan_button.fontMetrics().horizontalAdvance(text)
                                             for text in scan_labels) + 64)
        header.addWidget(self.add_button)
        header.addWidget(self.scan_button)
        self.scan_feedback = label("", "muted", True)
        self.scan_feedback.setAccessibleName(self.t("游戏扫描状态", "Game scan status"))
        self.scan_feedback.hide()
        layout.addWidget(self.scan_feedback)
        tools = row()
        self.search = QLineEdit()
        self.search.setPlaceholderText(self.t("搜索名称、平台或文件夹…    Ctrl+F", "Search games, platforms or folders…    Ctrl+F"))
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter)
        tools.addWidget(self.search, 1)
        self.installed_filter = ComboBox()
        self.installed_filter.addItems([self.t("全部游戏", "All games"), self.t("已安装", "Installed")])
        self.installed_filter.currentIndexChanged.connect(self._filter)
        tools.addWidget(self.installed_filter)
        self.arch_filter = ComboBox()
        for title, value in ((self.t("全部架构", "All architectures"), 0), ("64 bit", 64), ("32 bit", 32)):
            self.arch_filter.addItem(title, value)
        self.arch_filter.currentIndexChanged.connect(self._filter)
        tools.addWidget(self.arch_filter)
        layout.addLayout(tools)
        self.count_label = label("", "eyebrow")
        layout.addWidget(self.count_label)
        self.library_split = QSplitter(Qt.Orientation.Horizontal)
        self.library_split.setChildrenCollapsible(False)
        self.library_split.setHandleWidth(16)
        self.library_state = QStackedWidget()
        self.table = LibraryTable()
        self.table.setIconSize(QSize(32, 32))
        self.table.setModel(self.proxy)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(58)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col, width in ((1, 86), (2, 116), (3, 94)):
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
            self.table.setColumnWidth(col, width)
        self.table.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.table.setWordWrap(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 240)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.selectionModel().currentRowChanged.connect(self._select)
        self.library_state.addWidget(self.table)
        empty = QWidget()
        empty_layout = column(empty, 20, 10)
        empty_layout.addStretch()
        empty_layout.addWidget(EmptyArtwork(), alignment=Qt.AlignmentFlag.AlignHCenter)
        self.empty_title = label(self.t("尚未添加游戏", "No games added"), "subheading")
        self.empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self.empty_title)
        self.empty_description = label(self.t("扫描 Steam、Epic 等平台的已安装游戏，\n或手动选择游戏文件夹。", "Scan installed games from Steam, Epic and other platforms,\nor select a game folder."), "muted", True)
        self.empty_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self.empty_description)
        empty_layout.addSpacing(12)
        empty_layout.addWidget(button(self.t("扫描游戏", "Scan games"), self.scan, "primary"), alignment=Qt.AlignmentFlag.AlignHCenter)
        empty_layout.addStretch()
        self.library_state.addWidget(empty)
        self.library_split.addWidget(self.library_state)
        self.detail_stack = QStackedWidget()
        self.detail_stack.setMinimumWidth(310)
        self.detail_stack.setObjectName("detail")
        intro = QWidget()
        intro_layout = column(intro, 24, 14)
        intro_layout.addWidget(label(self.t("使用步骤", "INSTRUCTIONS"), "eyebrow"))
        intro_layout.addWidget(label(self.t("选择游戏后配置组件", "Select a game to configure components"), "subheading", True))
        for number, title, hint in (("01", self.t("添加游戏", "Add a game"), self.t("自动扫描或手动添加", "Scan automatically or add a folder")),
                                    ("02", self.t("选择安装配置", "Choose installation settings"), self.t("查看兼容性，选择安装路线和画质", "Check compatibility, route and quality")),
                                    ("03", self.t("安装并检查效果", "Install and verify"), self.t("安装后运行游戏，检查插件是否生效", "Run the game and check that the add-on works"))):
            intro_layout.addSpacing(10)
            intro_layout.addWidget(label(number, "badge"), alignment=Qt.AlignmentFlag.AlignLeft)
            intro_layout.addWidget(label(title))
            intro_layout.addWidget(label(hint, "muted", True))
        intro_layout.addStretch()
        intro_layout.addWidget(label(self.t("仅用于离线游戏。反作弊系统可能拦截 ReShade 插件。", "For offline games. Anti-cheat may flag ReShade add-ons."), "notice", True))
        self.detail_stack.addWidget(intro)
        self.detail_stack.addWidget(self._detail_panel())
        self.library_split.addWidget(self.detail_stack)
        self.library_split.setSizes([610, 350])
        layout.addWidget(self.library_split, 1)
        return page

    def _detail_panel(self):
        panel = QWidget()
        outer = column(panel, 0, 0)
        content = QWidget()
        layout = column(content, 20, 10)
        layout.addWidget(label(self.t("游戏设置", "GAME SETUP"), "eyebrow"))
        self.game_title = label("", "subheading", True)
        layout.addWidget(self.game_title)
        self.game_meta = label("", "muted", True)
        layout.addWidget(self.game_meta)
        self.compatibility = label("", "badge", True)
        layout.addWidget(self.compatibility)
        self.anticheat_warning = label("", "warning", True)
        self.anticheat_warning.hide()
        layout.addWidget(self.anticheat_warning)
        self.game_path = QLineEdit()
        self.game_path.setReadOnly(True)
        self.game_path.setStyleSheet("background: transparent; border: none; color: #929aa6; padding: 0; font-size: 11px;")
        layout.addWidget(self.game_path)
        self.route_combo = ComboBox()
        self.route_combo.currentIndexChanged.connect(self._route_changed)
        layout.addWidget(label(self.t("安装路线", "Installation route"), "muted"))
        layout.addWidget(self.route_combo)
        self.route_hint = label("", "muted", True)
        layout.addWidget(self.route_hint)
        layout.addWidget(label(self.t("仅用于离线游戏 · 不支持反作弊环境", "Offline games only · not for anti-cheat environments"), "muted", True))
        layout.addWidget(label(self.t("画质方案", "Quality profile"), "muted"))
        self.quality_combo = ComboBox()
        for text, key in ((self.t("画质优先", "Quality"), "Quality"), (self.t("均衡", "Balanced"), "Balanced"),
                          (self.t("性能优先", "Performance"), "Performance"), (self.t("自定义", "Custom"), "")):
            self.quality_combo.addItem(text, key)
        self.quality_combo.currentIndexChanged.connect(self._quality_changed)
        layout.addWidget(self.quality_combo)
        scale_row = row()
        self.scale_label = label(self.t("渲染区域", "Work area"), "muted")
        self.scale_value = label("100%", "muted")
        scale_row.addWidget(self.scale_label, 1)
        scale_row.addWidget(self.scale_value)
        layout.addLayout(scale_row)
        self.scale_slider = Slider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(50, 100)
        self.scale_slider.setSingleStep(5)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(lambda v: self.scale_value.setText(f"{v}%"))
        layout.addWidget(self.scale_slider)
        self.keep_dlss = QCheckBox(self.t("保留游戏自带的 DLSS", "Keep the game's own DLSS"))
        self.keep_dlss.setChecked(True)
        layout.addWidget(self.keep_dlss)
        self.advanced_toggle = QToolButton()
        self.advanced_toggle.setText(self.t("高级设置", "Advanced settings"))
        self.advanced_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.advanced_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.advanced_toggle.setCheckable(True)
        layout.addWidget(self.advanced_toggle)
        self.advanced = QWidget()
        form = QFormLayout(self.advanced)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(10)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.exe_combo = ComboBox()
        self.exe_combo.activated.connect(self._exe_changed)
        form.addRow(self.t("目标程序", "Executable"), self.exe_combo)
        self.api_combo = ComboBox()
        self.api_combo.addItem(self.t("自动检测", "Automatic"), "")
        for api in ("DX9", "DX10", "DX11", "DX12", "Vulkan", "OpenGL"):
            self.api_combo.addItem(api, api)
        self.api_combo.activated.connect(self._api_changed)
        form.addRow(self.t("图形接口", "Graphics API"), self.api_combo)
        self.fg_check = QCheckBox(self.t("FSR 补帧 · 2x", "FSR frame generation · 2x"))
        self.fg_check.setToolTip(self.t("OptiScaler / DX12。请关闭游戏内补帧；可能增加延迟。", "OptiScaler / DX12. Disable in-game frame generation; may add latency."))
        form.addRow(self.fg_check)
        self.mfg_check = QCheckBox(self.t("RTX 40 MFG（实验性）", "RTX 40 MFG (experimental)"))
        self.mfg_check.setToolTip(self.t("需游戏自带 DLSS 补帧并保持开启。在 ReShade 面板选择 3x/4x；可能产生画面错误或崩溃。", "Requires the game's DLSS frame generation enabled. Select 3x/4x in ReShade; may cause artifacts or crashes."))
        form.addRow(self.mfg_check)
        self.provider_combo = ComboBox()
        for key, value in reshade_ini.PROVIDERS.items():
            self.provider_combo.addItem(value[0], key)
        form.addRow(self.t("运动矢量", "Motion vectors"), self.provider_combo)
        self.preset_combo = ComboBox()
        for key, value in feedcfg.PRESETS.items():
            self.preset_combo.addItem(value, key)
        form.addRow(self.t("DLSS 预设", "DLSS preset"), self.preset_combo)
        self.hdr_combo = ComboBox()
        for key, value in feedcfg.HDR.items():
            self.hdr_combo.addItem(value, key)
        form.addRow("HDR", self.hdr_combo)
        self.nr_preset = ComboBox()
        for key, value in optiscaler.NR_PRESETS.items():
            self.nr_preset.addItem(str(value), key)
        form.addRow(self.t("NR 模型", "NR model"), self.nr_preset)
        self.nr_style = ComboBox()
        for key, value in optiscaler.NR_STYLES.items():
            self.nr_style.addItem(str(value), key)
        form.addRow(self.t("NR 风格", "NR style"), self.nr_style)
        self.proxy_combo = ComboBox()
        self.proxy_combo.addItem(self.t("自动选择", "Automatic"), "")
        for value in installer.RESHADE_PROXIES:
            self.proxy_combo.addItem(value, value)
        form.addRow(self.t("ReShade 加载名称", "ReShade proxy"), self.proxy_combo)
        self.opti_proxy = ComboBox()
        self.opti_proxy.addItem(self.t("自动选择", "Automatic"), "")
        for value in optiscaler.PROXY_NAMES:
            self.opti_proxy.addItem(value, value)
        form.addRow(self.t("OptiScaler 加载名称", "OptiScaler proxy"), self.opti_proxy)
        self.dxvk_check = QCheckBox("DXVK  ·  DirectX → Vulkan")
        form.addRow(self.dxvk_check)
        self.remix_swap = QCheckBox(self.t("替换 Remix 运行时（实验性）", "Replace Remix runtime (experimental)"))
        form.addRow(self.remix_swap)
        self.version_combos = {}
        for key, title in (("renodx", "DLSS 5 add-on"), ("dlssnr", "nvngx_dlssnr"), ("dlss", "nvngx_dlss")):
            combo = ComboBox()
            combo.addItem(self.t("自动 / 推荐版本", "Automatic / recommended"), None)
            self.version_combos[key] = combo
            if key == "renodx":
                combo.activated.connect(self._online_addon)
            form.addRow(title, combo)
        self.feeder_combo = ComboBox()
        self.feeder_combo.addItem(self.t("最新正式版", "Latest stable"), "")
        self.feeder_combo.addItem(self.t("最新预览版", "Latest preview"), "__pre__")
        form.addRow("Feeder", self.feeder_combo)
        form.addRow(button(self.t("加载版本列表", "Load available versions"), self.load_catalog))
        self.local_file_button = button(self.t("使用本地插件…", "Use local add-on…"), self.choose_addon)
        form.addRow(self.local_file_button)
        self.local_addon = None
        profile_row = row()
        profile_row.addWidget(button(self.t("保存方案", "Save profile"), self.save_profile))
        profile_row.addWidget(button(self.t("载入方案", "Load profile"), self.load_profile))
        form.addRow(profile_row)
        form.addRow(button(self.t("删除自定义方案…", "Delete custom profile…"), self.delete_profile, "ghost"))
        self.advanced.hide()
        self.advanced_toggle.toggled.connect(self._advanced)
        layout.addWidget(self.advanced)
        layout.addStretch()
        outer.addWidget(scroller(content), 1)
        actions = QWidget()
        action_layout = column(actions, 16, 8)
        self.install_button = button(self.t("安装 DLSS 5", "Install DLSS 5"), self.install_selected, "primary")
        self.install_button.setMinimumHeight(42)
        action_layout.addWidget(self.install_button)
        tools = row()
        self.preview_button = button(self.t("预览变更", "Preview"), self.preview, "ghost")
        self.more_button = button(self.t("更多操作 ···", "More ···"), self.more_actions, "ghost")
        tools.addWidget(self.preview_button)
        tools.addWidget(self.more_button)
        action_layout.addLayout(tools)
        outer.addWidget(actions)
        return panel

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def focus_search(self):
        self.navigate(0)
        self.search.setFocus()

    def _filter(self, *args):
        if not hasattr(self, "count_label"):
            return
        self.proxy.set_query(self.search.text(), self.installed_filter.currentIndex() == 1,
                             self.arch_filter.currentData() or 0)
        count = self.proxy.rowCount()
        installed = sum(e.installed for e in self.model.entries)
        self.count_label.setText(self.t(f"{count} 款游戏   /   {installed} 款已安装", f"{count} GAMES   /   {installed} INSTALLED"))
        self.library_state.setCurrentIndex(0 if count else 1)
        if self.model.entries and not count:
            self.empty_title.setText(self.t("没有匹配的游戏", "No matching games"))
            self.empty_description.setText(self.t("换个关键词，或清除筛选条件。", "Try another keyword or clear the filters."))
        else:
            self.empty_title.setText(self.t("尚未添加游戏", "No games added"))
        # A hidden selection must never leave an actionable stale game panel.
        if self.current and not any(self.proxy.index(i, 0).data(Qt.ItemDataRole.UserRole).key == self.current.key for i in range(count)):
            self.current = None
            self.inspection = None
            self.selection_generation += 1
            self.detail_stack.setCurrentIndex(0)

    def _submit(self, work, done=None, busy=False, title=""):
        if busy and self.busy_job is not None:
            return None
        job_id = self.jobs.submit(work)
        self.callbacks[job_id] = (done, busy, title)
        if busy:
            self.busy_job = job_id
            self._set_busy(True)
            self.status.setText(title)
            self.activity_title.setText(title)
            self.progress.setRange(0, 0)
        return job_id

    def _completed(self, job_id, result, error):
        was_scan = job_id == self.scan_job
        if was_scan:
            self.scan_job = None
            self.scan_button.set_loading(False)
            self.scan_button.setText(self.t("重新扫描", "Rescan"))
            self.scan_button.setToolTip(self.t("重新扫描游戏库", "Rescan the game library"))
            if error:
                self.scan_feedback.setText(self.t("扫描失败，已保留原游戏列表。可重试，或在任务与日志中查看原因。", "Scan failed. Your previous library is unchanged. Retry or check Activity for details."))
        self.language.setEnabled(not self.jobs.active)
        done, busy, title = self.callbacks.pop(job_id, (None, False, ""))
        if busy:
            self.busy_job = None
            self._set_busy(False)
            self.progress.setRange(0, 100)
            self.progress.setValue(0 if error else 100)
        if error:
            self._append_log(error[1])
            self.status.setText(self.t("操作失败 · 查看任务日志", "Failed · see Activity"))
            if busy:
                self.show_text(self.t("操作未完成", "Operation failed"), error[0])
            return
        if busy:
            self.status.setText(self.t("●  已完成", "●  Complete"))
        if done:
            done(result)

    def _events(self, events):
        lines = []
        progress = None
        for job_id, kind, value in events:
            if kind == "log":
                lines.append(str(value))
            elif kind == "progress" and job_id == self.busy_job:
                progress = value
        if lines:
            self._append_log("\n".join(lines))
        if progress:
            value, message = progress
            self.progress.setRange(0, 100)
            self.progress.setValue(max(0, min(100, int(value))))
            self.activity_title.setText(str(message))

    def _append_log(self, text):
        self.log_lines.extend(str(text).splitlines())
        self.log_lines = self.log_lines[-3000:]
        self.activity_log.appendPlainText(str(text))

    def _set_busy(self, busy):
        self.scan_button.setEnabled(not busy)
        self.add_button.setEnabled(not busy)
        self.language.setEnabled(not self.jobs.active)
        self.detail_stack.widget(1).setEnabled(not busy)
        self.install_button.setEnabled(not busy and self._detail_ready and self._route_usable())

    def _hardware(self, result):
        self.gpu_label.setText(result[0] or self.t("未检测到 NVIDIA 显卡", "No NVIDIA GPU detected"))
        self.language.setEnabled(not self.jobs.active)

    def scan(self):
        if self.busy_job is not None:
            return
        self.scan_feedback.setText(self.t("正在扫描本地游戏，完成后会更新列表。", "Scanning local games. The library will update when finished."))
        self.scan_feedback.show()
        self.scan_button.setText(self.t("扫描中…", "Scanning…"))
        self.scan_button.setToolTip(self.t("正在扫描，请稍候。", "Scan in progress. Please wait."))
        self.scan_button.set_loading(True)
        self.scan_job = self._submit(self.service.scan, self._scan_finished, busy=True,
            title=self.t("正在扫描本地游戏…", "Scanning local libraries…"))

    def _scan_finished(self, entries):
        self._scanned(entries)
        message = self.t(f"扫描完成，找到 {len(entries)} 款游戏。", f"Scan complete. Found {len(entries)} games.") if entries else self.t(
            "扫描完成，未找到游戏。可以手动添加游戏目录。", "Scan complete. No games found. You can add a game folder manually.")
        self.scan_feedback.setText(message)
        self.status.setText(message)
        self.activity_title.setText(message)

    def _scanned(self, entries):
        self.current = None
        self.inspection = None
        self.selection_generation += 1
        self.detail_stack.setCurrentIndex(0)
        self.model.replace(entries)
        self._filter()
        self.navigate(0)

    def add_game(self):
        if self.busy_job:
            return
        folder = QFileDialog.getExistingDirectory(self, self.t("选择游戏文件夹", "Choose game folder"))
        if folder:
            self._submit(lambda emit: self.service.manual(folder), self._added, busy=True,
                         title=self.t("正在识别游戏…", "Inspecting game…"))

    def _added(self, entry):
        entries = [e for e in self.model.entries if e.key != entry.key] + [entry]
        self.model.replace(entries)
        self.search.clear()
        self.installed_filter.setCurrentIndex(0)
        self.arch_filter.setCurrentIndex(0)
        self._filter()
        self.navigate(0)
        for i in range(self.proxy.rowCount()):
            if self.proxy.index(i, 0).data(Qt.ItemDataRole.UserRole).key == entry.key:
                self.table.selectRow(i)
                break

    def _select(self, index, previous):
        if not index.isValid():
            return
        entry = index.data(Qt.ItemDataRole.UserRole)
        self.current = entry
        self.inspection = None
        self._detail_ready = False
        self.selection_generation += 1
        generation = self.selection_generation
        self.game_title.setText(entry.game.name)
        self.game_meta.setText(f"{entry.game.source}  ·  {entry.game.api}  ·  {entry.game.bitness or '?'} bit")
        self.game_path.setText(str(entry.game.folder))
        self.compatibility.setText(self.t("正在检查兼容性…", "Checking compatibility…"))
        self.anticheat_warning.setText(self.t(f"检测到 {entry.anticheat}。插件可能被拦截、导致游戏无法启动或封禁账号。请勿用于联网模式。", f"{entry.anticheat} detected. Add-ons may be blocked, prevent launch or cause bans. Do not use online."))
        self.anticheat_warning.setVisible(bool(entry.anticheat))
        self.detail_stack.setCurrentIndex(1)
        self.install_button.setEnabled(False)
        self.preview_button.setEnabled(False)
        self.more_button.setEnabled(False)
        self._submit(lambda emit: self.service.inspect(entry),
                     lambda inspection: self._inspected(inspection, generation))

    def _inspected(self, inspection, generation):
        if generation != self.selection_generation:
            return
        self.inspection = inspection
        entry = inspection.entry
        self.anticheat_warning.setText(self.t(f"检测到 {entry.anticheat}。插件可能被拦截、导致游戏无法启动或封禁账号。请勿用于联网模式。", f"{entry.anticheat} detected. Add-ons may be blocked, prevent launch or cause bans. Do not use online."))
        self.anticheat_warning.setVisible(bool(entry.anticheat))
        self.options = inspection.options
        self._detail_ready = True
        self.route_combo.blockSignals(True)
        self.route_combo.clear()
        for route in inspection.support.options:
            suffix = self.t(" · 推荐", " · Recommended") if route == inspection.support.recommended else ""
            self.route_combo.addItem(route.title() + suffix, route)
        self.route_combo.blockSignals(False)
        self.exe_combo.blockSignals(True)
        self.exe_combo.clear()
        for candidate in inspection.entry.game.candidates or [inspection.entry.game.exe]:
            if candidate:
                self.exe_combo.addItem(candidate.name, str(candidate))
        self.exe_combo.setCurrentIndex(max(0, self.exe_combo.findData(str(inspection.entry.game.exe))))
        self.exe_combo.blockSignals(False)
        self._apply_options(inspection.options)
        self._combo(self.api_combo, inspection.api_override)
        self.preview_button.setEnabled(True)
        self.more_button.setEnabled(True)
        self.gpu_label.setText(inspection.gpu_name or self.t("未检测到 NVIDIA 显卡", "No NVIDIA GPU detected"))
        self._set_busy(self.busy_job is not None)

    @staticmethod
    def _combo(combo, value):
        index = combo.findData(value)
        if index < 0 and value not in (None, ""):
            combo.addItem(str(value), value)
            index = combo.count() - 1
        combo.setCurrentIndex(max(0, index))

    def _apply_options(self, options):
        self.options = replace(options, feed=dict(options.feed), nr=dict(options.nr))
        self.route_combo.blockSignals(True)
        self._combo(self.route_combo, options.path)
        self.route_combo.blockSignals(False)
        # Configure the route's family and range before restoring saved values.
        self._route_changed()
        self.keep_dlss.setChecked(options.keep_game_dlss)
        self.dxvk_check.setChecked(options.dxvk)
        self.remix_swap.setChecked(options.remix_swap)
        self.fg_check.setChecked(options.fg)
        self.mfg_check.setChecked(options.mfg)
        for combo, value in ((self.provider_combo, options.provider), (self.preset_combo, options.feed.get("preset", next(iter(feedcfg.PRESETS)))),
                             (self.hdr_combo, options.feed.get("hdr", next(iter(feedcfg.HDR)))), (self.proxy_combo, options.reshade_proxy),
                             (self.opti_proxy, options.opti_proxy), (self.nr_preset, options.nr.get("Preset", 0)),
                             (self.nr_style, options.nr.get("Style", 0))):
            self._combo(combo, value)
        self.quality_combo.setCurrentIndex(3)
        scale = options.nr.get("WorkingScale", 1) * 100 if options.path == dlss.OPTI else options.feed.get("work_resolution", 100)
        self.scale_slider.setValue(int(scale))
        for key, combo in self.version_combos.items():
            self._combo(combo, getattr(options, key))
        self._combo(self.feeder_combo, options.feeder_tag or ("__pre__" if options.feeder_prerelease else ""))
        self.local_addon = options.renodx_local
        self._local_addon_label()
        self._route_changed()

    def _options(self):
        route = self.route_combo.currentData() or self.options.path
        feed, nr = dict(self.options.feed), dict(self.options.nr)
        if route == dlss.OPTI:
            nr.update(WorkingScale=self.scale_slider.value() / 100,
                      Preset=self.nr_preset.currentData(), Style=self.nr_style.currentData())
        elif self.scale_slider.isEnabled():
            feed["work_resolution"] = self.scale_slider.value()
        if self.preset_combo.currentData() is not None:
            feed["preset"] = self.preset_combo.currentData()
        if self.hdr_combo.currentData() is not None:
            feed["hdr"] = self.hdr_combo.currentData()
        feeder = self.feeder_combo.currentData() or ""
        return replace(self.options, path=route, keep_game_dlss=self.keep_dlss.isChecked(),
                       provider=self.provider_combo.currentData(), feed=feed, nr=nr,
                       dxvk=self.dxvk_check.isChecked(), remix_swap=self.remix_swap.isChecked(),
                       fg=self.fg_check.isEnabled() and self.fg_check.isChecked(),
                       mfg=self.mfg_check.isEnabled() and self.mfg_check.isChecked(),
                       renodx_local=self.local_addon, reshade_proxy=self.proxy_combo.currentData() or "",
                       opti_proxy=self.opti_proxy.currentData() or "", feeder_prerelease=feeder == "__pre__",
                       feeder_tag="" if feeder == "__pre__" else feeder,
                       **{key: combo.currentData() for key, combo in self.version_combos.items()})

    def _route_usable(self):
        return bool(self.inspection and self.inspection.support.supported and
                    self.inspection.fit.get(self.route_combo.currentData(), (False, ""))[0])

    def _route_changed(self, *args):
        if not self.inspection:
            return
        route = self.route_combo.currentData()
        family = "renodx_sf" if route == dlss.RENODX else "renodx"
        if family != self.addon_family:
            self.addon_family = family
            self._fill_addon_versions()
            self.local_addon = None
            self._local_addon_label()
        usable, reason = self.inspection.fit.get(route, (False, ""))
        level, explanation = self.inspection.levels.get(route, (self.inspection.level, self.inspection.explanation))
        names = {"stable": self.t("兼容性较好", "Stable route"), "beta": self.t("测试版支持", "Beta support"),
                 "experimental": self.t("实验性支持", "Experimental")}
        self.compatibility.setText(names.get(level, level) if usable else self.t("当前硬件或游戏不支持", "Unavailable for this setup"))
        self.compatibility.setToolTip(reason + "\n" + explanation)
        self.route_hint.setText(self.t("此路线支持当前游戏和显卡。", "This route supports the current game and GPU.") if usable else reason)
        self.route_hint.setVisible(not usable)
        self.route_hint.setToolTip(reason)
        work = route == dlss.OPTI or (route == dlss.FEEDER and
            self.current.game.api == "DX11" and self.current.game.bitness == 64)
        self.scale_slider.setRange(optiscaler.NR_SCALE_MIN if route == dlss.OPTI else 50,
                                   optiscaler.NR_SCALE_MAX if route == dlss.OPTI else 100)
        self.scale_slider.setEnabled(work)
        self.scale_label.setText(self.t("渲染区域", "Work area") if work else self.t("此路线由游戏控制画质", "Quality controlled in game"))
        self.nr_preset.setEnabled(route == dlss.OPTI)
        self.nr_style.setEnabled(route == dlss.OPTI)
        self.opti_proxy.setEnabled(route == dlss.OPTI)
        self.fg_check.setEnabled(route == dlss.OPTI and self.current.game.api == "DX12")
        self.mfg_check.setEnabled(self.inspection.mfg_available and route not in (dlss.OPTI, dlss.REMIX))
        if not self.fg_check.isEnabled():
            self.fg_check.setChecked(False)
        if not self.mfg_check.isEnabled():
            self.mfg_check.setChecked(False)
        self.remix_swap.setVisible(route == dlss.REMIX)
        self.install_button.setText(self.t("重新安装 / 更新", "Reinstall / update") if self.current.installed else self.t("安装 DLSS 5", "Install DLSS 5"))
        self.install_button.setEnabled(usable and self.busy_job is None)

    def _quality_changed(self, *args):
        name = self.quality_combo.currentData()
        if name and self.inspection:
            values = profiles.BUILTINS[name]
            value = values["nr"]["WorkingScale"] * 100 if self.route_combo.currentData() == dlss.OPTI else values["feed"]["work_resolution"]
            self.scale_slider.setValue(int(value))

    def _advanced(self, visible):
        self.advanced.setVisible(visible)
        self.advanced_toggle.setArrowType(Qt.ArrowType.DownArrow if visible else Qt.ArrowType.RightArrow)

    def _exe_changed(self, index):
        if not self.current or self.busy_job:
            return
        path = self.exe_combo.currentData()
        entry = self.current
        self._submit(lambda emit: self.service.select_executable(entry, path), self._added, busy=True,
                     title=self.t("重新识别目标程序…", "Inspecting executable…"))

    def _api_changed(self, index):
        if not self.current or self.busy_job:
            return
        entry, api = self.current, self.api_combo.currentData()
        self._submit(lambda emit: self.service.set_graphics_api(entry, api), self._added,
                     busy=True, title=self.t("正在重新检测…", "Updating detection…"))

    def _confirm_anticheat(self, entries):
        flagged = [e.game.name for e in entries if e.anticheat]
        if not flagged:
            return True
        message = self.t("以下游戏检测到反作弊：\n", "Anti-cheat detected in:\n") + "\n".join(flagged)
        message += self.t("\n\n安装插件可能导致无法启动或封禁账号。请勿用于联网模式。仍要继续？",
                          "\n\nAdd-ons may prevent launch or cause bans. Do not use online. Continue?")
        return QMessageBox.warning(self, self.t("反作弊风险", "Anti-cheat risk"), message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes

    def install_selected(self):
        if not self.current or not self._route_usable() or self.busy_job:
            return
        entry, options = self.current, self._options()
        if not self._confirm_anticheat([entry]):
            return
        self._submit(lambda emit: self.service.install(entry, options, emit),
                     lambda report: self._installed(entry, report), busy=True,
                     title=self.t("正在安装 · 可在任务页查看进度", "Installing · progress in Activity"))
        self.navigate(2)

    def _installed(self, entry, report):
        entry.installed = True
        self.model.refresh()
        self._route_changed()
        self._filter()
        self._append_log(self.t("安装完成。先设置游戏分辨率，再开启神经渲染。", "Installed. Set the game resolution before enabling neural rendering."))
        if report.warnings:
            self._append_log("\n".join(report.warnings))
        self.show_text(self.t("安装完成", "Installation complete"),
            self.t("请以无边框或全屏模式运行游戏。ReShade 路线：按 Home 打开面板，F6 开关神经渲染。Remix 路线：按 Alt+X 打开 Remix 设置。\n\n32 位游戏请使用游戏内面板，不要切换到辅助进程窗口。", "Use borderless or fullscreen. ReShade routes: Home opens the overlay; F6 toggles neural rendering. Remix: Alt+X opens settings.\nFor 32-bit games, use the in-game overlay, not the helper window.") + "\n\n" + "\n".join(report.warnings))

    def uninstall_selected(self):
        if not self.current or not self.current.installed or self.busy_job:
            return
        entry = self.current
        if QMessageBox.question(self, self.t("卸载", "Uninstall"), self.t(f"卸载 {entry.game.name} 的增强组件并恢复备份？", f"Remove installed components and restore backups for {entry.game.name}?")) != QMessageBox.StandardButton.Yes:
            return
        def done(result):
            entry.installed = False
            self.model.refresh()
            self._append_log("\n".join(result))
            self._filter()
            self._route_changed()
        self._submit(lambda emit: self.service.uninstall(entry, emit), done, busy=True, title=self.t("正在卸载…", "Uninstalling…"))

    def preview(self):
        if self.current and self.inspection:
            entry, options = self.current, self._options()
            self._submit(lambda emit: self.service.preview(entry, options),
                         lambda result: self.show_text(self.t("安装变更预览", "Installation preview"), result),
                         busy=True, title=self.t("正在生成预览…", "Preparing preview…"))

    def more_actions(self):
        if not self.current or not self.inspection or self.busy_job:
            return
        menu = QMenu(self)
        for title, callback in ((self.t("诊断安装问题", "Diagnose"), lambda: self._report(self.service.diagnose)),
                                (self.t("检查组件版本", "Component versions"), lambda: self._report(self.service.versions)),
                                (self.t("截图效果对比", "Screenshot comparison"), self.show_comparison),
                                (self.t("打开游戏文件夹", "Open game folder"), lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.current.game.folder))))):
            menu.addAction(title, callback)
        menu.addSeparator()
        action = menu.addAction(self.t("卸载增强组件", "Uninstall components"), self.uninstall_selected)
        action.setEnabled(self.current.installed)
        menu.exec(self.more_button.mapToGlobal(self.more_button.rect().bottomLeft()))

    def _report(self, function):
        entry = self.current
        if entry:
            self._submit(lambda emit: function(entry), lambda text: self.show_text(self.t("检查结果", "Results"), text),
                         busy=True, title=self.t("正在检查…", "Checking…"))

    def show_text(self, title, text):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(700, 500)
        layout = column(dialog, 22)
        layout.addWidget(label(title, "subheading"))
        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setPlainText(str(text))
        layout.addWidget(output, 1)
        layout.addWidget(button(self.t("关闭", "Close"), dialog.accept), alignment=Qt.AlignmentFlag.AlignRight)
        dialog.exec()

    def load_catalog(self):
        def done(result):
            catalog, releases = result
            self.catalog = catalog
            for key, combo in self.version_combos.items():
                selected = combo.currentData()
                combo.clear()
                combo.addItem(self.t("自动 / 推荐版本", "Automatic / recommended"), None)
                for item in catalog.get(self.addon_family if key == "renodx" else key, []):
                    combo.addItem(item["label"], item["label"])
                self._combo(combo, selected)
            for tag, preview in releases:
                if self.feeder_combo.findData(tag) < 0:
                    self.feeder_combo.addItem(tag, tag)
            self.catalog_loaded = True
        self._submit(lambda emit: self.service.catalog(), done, busy=True, title=self.t("正在获取版本…", "Loading versions…"))

    def _fill_addon_versions(self):
        combo = self.version_combos["renodx"]
        combo.clear()
        combo.addItem(self.t("自动 / 推荐版本", "Automatic / recommended"), None)
        for item in self.catalog.get(self.addon_family, []):
            combo.addItem(item["label"], item["label"])

    def _online_addon(self, index):
        self.local_addon = None
        self._local_addon_label()

    def _local_addon_label(self):
        self.local_file_button.setText(Path(self.local_addon).name if self.local_addon else self.t("使用本地插件…", "Use local add-on…"))
        self.local_file_button.setToolTip(str(self.local_addon or ""))

    def choose_addon(self):
        filename, _ = QFileDialog.getOpenFileName(self, self.t("选择本地插件", "Choose local add-on"), "", "ReShade add-on (*.addon64)")
        if filename:
            self.local_addon = Path(filename)
            self._local_addon_label()

    def save_profile(self):
        name, ok = QInputDialog.getText(self, self.t("保存方案", "Save profile"), self.t("方案名称", "Profile name"))
        if ok and name.strip():
            options = self._options()
            self._submit(lambda emit: profiles.save(name, options), busy=True, title=self.t("正在保存…", "Saving…"))

    def load_profile(self):
        def done(names):
            name, ok = QInputDialog.getItem(self, self.t("载入方案", "Load profile"), self.t("选择方案", "Choose profile"), names, editable=False)
            if ok:
                base = self._options()
                generation = self.selection_generation
                self._submit(lambda emit: profiles.apply(base, profiles.load(name)),
                             lambda options: self._apply_options(options) if generation == self.selection_generation else None,
                             busy=True, title=self.t("正在载入…", "Loading…"))
        self._submit(lambda emit: profiles.list_profiles(), done)

    def delete_profile(self):
        def done(names):
            if not names:
                self.show_text(self.t("暂无自定义方案", "No custom profiles"), self.t("内置方案不能删除。", "Built-in profiles cannot be removed."))
                return
            name, ok = QInputDialog.getItem(self, self.t("删除方案", "Delete profile"), self.t("选择要删除的方案", "Choose the profile to remove"), names, editable=False)
            if ok:
                self._submit(lambda emit: profiles.delete(name), busy=True, title=self.t("正在删除…", "Deleting…"))
        self._submit(lambda emit: [name for name in profiles.list_profiles() if not profiles.is_builtin(name)], done)

    def change_language(self, index):
        if self.jobs.active:
            self.language.blockSignals(True)
            self.language.setCurrentIndex(0 if self.chinese else 1)
            self.language.blockSignals(False)
            return
        options = self._options() if self.inspection else None
        selected, inspection, page = self.current, self.inspection, self.pages.currentIndex()
        self.chinese = index == 0
        prefs.set_("language", "zh_CN" if self.chinese else "en")
        old = self.takeCentralWidget()
        self._build()
        old.deleteLater()
        self.current, self.inspection = selected, inspection
        if inspection:
            self.game_title.setText(selected.game.name)
            self.game_path.setText(str(selected.game.folder))
            self.detail_stack.setCurrentIndex(1)
            self._inspected(inspection, self.selection_generation)
            self._apply_options(options)
        self.navigate(page)
        self.activity_log.setPlainText("\n".join(self.log_lines))

    def _activity_page(self):
        page = QWidget()
        layout = column(page, 28, 18)
        header = self._page_header(layout, self.t("任务与日志", "Activity"), self.t("查看任务进度、结果和错误日志。", "View task progress, results and errors."))
        header.addWidget(button(self.t("复制日志", "Copy log"), lambda: QApplication.clipboard().setText(self.activity_log.toPlainText())))
        self.activity_title = label(self.t("暂无运行中的任务", "No task running"), "subheading")
        layout.addWidget(self.activity_title)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setValue(0)
        self.progress.setFixedHeight(4)
        layout.addWidget(self.progress)
        self.activity_log = QPlainTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setMaximumBlockCount(3000)
        self.activity_log.setPlaceholderText(self.t("暂无日志。", "No logs yet."))
        layout.addWidget(self.activity_log, 1)
        return page

    def _settings_page(self):
        page = QWidget()
        layout = column(page, 28, 22)
        self._page_header(layout, self.t("设置", "Settings"), self.t("查看版本和更新说明，更新已安装的组件。", "View versions and update instructions, or update installed components."))
        layout.addWidget(label(self.t("应用更新", "Application updates"), "subheading"))
        self.product_update_status = label(self.t("检查 JustDLSS5 新版本。", "Check for a new JustDLSS5 release."), "muted", True)
        layout.addWidget(self.product_update_status)
        self.auto_update_check = QCheckBox(self.t("启动时检查更新（每天最多一次）", "Check on startup (at most once a day)"))
        self.auto_update_check.setChecked(bool(prefs.get("product_update_check", True)))
        self.auto_update_check.toggled.connect(lambda checked: prefs.set_("product_update_check", checked))
        layout.addWidget(self.auto_update_check)
        self.preview_update_check = QCheckBox(self.t("包含预发布版本", "Include prereleases"))
        self.preview_update_check.setChecked(bool(prefs.get("product_update_preview", False)))
        self.preview_update_check.toggled.connect(lambda checked: prefs.set_("product_update_preview", checked))
        layout.addWidget(self.preview_update_check)
        layout.addWidget(button(self.t("检查应用更新", "Check for updates"), self.check_product_update), alignment=Qt.AlignmentFlag.AlignLeft)
        card = QFrame()
        card.setObjectName("card")
        content = column(card, 24, 12)
        content.addWidget(label(self.t("更新安装引擎", "Update the installation engine"), "subheading"))
        content.addWidget(label(self.t("按更新说明更新安装引擎，保留当前界面。更新前会检查兼容性并备份旧版本。", "Follow the instructions to update the installation engine while keeping this interface. Updates are checked for compatibility and the previous version is backed up."), "muted", True))
        content.addWidget(label(f"{NAME} {VERSION}   /   Core {update.VERSION}", "badge"), alignment=Qt.AlignmentFlag.AlignLeft)
        content.addWidget(button(self.t("打开更新说明", "Update instructions"), self.open_update_guide), alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(card)
        layout.addWidget(label(self.t("维护", "MAINTENANCE"), "eyebrow"))
        layout.addWidget(button(self.t("重新安装所有游戏的组件", "Reinstall components for all games"), self.update_all), alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(label(self.t("窗口大小自动保存。Ctrl+F 搜索游戏。拖动游戏列表与设置之间的分隔线可调整空间。", "Window size is remembered. Ctrl+F focuses search. Drag the divider to adjust library and setup widths."), "muted", True))
        layout.addStretch()
        return scroller(page)

    def open_update_guide(self):
        path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)) / "docs/MAINTAINING.zh-CN.md"
        if path.is_file():
            self.show_text(self.t("更新说明", "Update guide"), path.read_text(encoding="utf8"))

    def report_problem(self):
        fields = feedback.report_fields(update.VERSION, self.current, self.inspection,
            self.route_combo.currentData() or "" if self.current else "")
        titles = {"versions": self.t("版本", "Versions"), "platform": "Windows",
                  "game": self.t("游戏", "Game"), "store": self.t("游戏来源", "Store"),
                  "configuration": self.t("配置", "Configuration"), "hardware": self.t("显卡与驱动", "GPU and driver")}
        preview = "\n\n".join(f"{titles[key]}: {value}" for key, value in fields.items())
        dialog = QMessageBox(self)
        dialog.setWindowTitle(self.t("反馈问题", "Report a problem"))
        dialog.setText(self.t("将在 GitHub 打开反馈表单，预填以下信息。截图和日志由你选择添加，提交前可修改。私有仓库需要访问权限。",
            "Open a GitHub form with the details below. Review before submitting; add screenshots and logs yourself. Private repositories require access."))
        dialog.setInformativeText(preview)
        dialog.setStandardButtons(QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Cancel)
        if dialog.exec() == QMessageBox.StandardButton.Open:
            if not QDesktopServices.openUrl(QUrl(feedback.issue_url(fields))):
                self.show_text(self.t("无法打开浏览器", "Could not open browser"), feedback.issue_url(fields))

    def check_product_update(self, checked=False, automatic=False):
        if self.update_check_running:
            return
        self.update_check_running = True
        prefs.set_("product_update_checked", time.time())
        preview = bool(prefs.get("product_update_preview", False))
        self.product_update_status.setText(self.t("正在检查…", "Checking…"))
        def done(result):
            self.update_check_running = False
            messages = {
                "current": self.t("当前已是最新版本。", "You are up to date."),
                "no_release": self.t("所选渠道尚无发行版本。", "No releases in the selected channel."),
                "restricted": self.t("无法读取发行信息：仓库可能为私有、尚无发行版或请求受限。可在浏览器登录 GitHub 后查看。", "Release information is inaccessible: private repository, no release or API limit. Check GitHub in your browser."),
                "unavailable": self.t("更新检查失败，请稍后重试。", "Update check failed. Try again later."),
                "available": self.t(f"发现 {result.version}，可查看更新说明。", f"{result.version} is available. View the release notes."),
            }
            self.product_update_status.setText(messages.get(result.status, messages["unavailable"]))
            if result.status == "available":
                self.status.setText(self.product_update_status.text())
                if not automatic and QMessageBox.question(self, self.t("发现新版本", "Update available"),
                    self.t(f"打开 {result.version} 的发行页面？", f"Open the release page for {result.version}?")) == QMessageBox.StandardButton.Yes:
                    QDesktopServices.openUrl(QUrl(result.url))
        self._submit(lambda emit: updates.check(preview), done)

    def update_all(self):
        entries = [entry for entry in self.model.entries if entry.installed]
        if not self._confirm_anticheat(entries):
            return
        if not entries:
            self.show_text(self.t("无需更新", "Nothing to update"), self.t("请先扫描游戏库。", "Scan the library first."))
            return
        if QMessageBox.question(self, self.t("更新全部", "Update all"), self.t(f"使用原安装配置重新安装 {len(entries)} 款游戏的组件？", f"Reinstall components for {len(entries)} games using their saved settings?")) == QMessageBox.StandardButton.Yes:
            self._submit(lambda emit: self.service.update_all(entries, emit), busy=True, title=self.t("正在更新组件…", "Updating components…"))
            self.navigate(2)

    def _video_page(self):
        page = QWidget()
        layout = column(page, 28, 20)
        self._page_header(layout, self.t("视频增强", "Video studio"), self.t("播放、下载或增强视频，也可处理摄像头画面。", "Play, download or enhance videos, or process camera input."))
        card = QFrame()
        card.setObjectName("card")
        content = column(card, 24, 14)
        content.addWidget(label(self.t("安装播放器", "Install the player"), "subheading"))
        content.addWidget(label(self.t("安装便携版 MPC-HC 后，在游戏库为播放器安装 DLSS 5。", "Set up portable MPC-HC, then install DLSS 5 for it from the library."), "muted", True))
        content.addWidget(button(self.t("配置播放器…", "Set up player…"), self.setup_video, "primary"), alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(card)
        layout.addWidget(label(self.t("播放", "PLAYBACK"), "eyebrow"))
        self.video_url = QLineEdit()
        self.video_url.setPlaceholderText(self.t("粘贴 YouTube 或其他视频链接…", "Paste a YouTube or video URL…"))
        layout.addWidget(self.video_url)
        playback = row()
        for text, action in ((self.t("播放链接", "Play URL"), "url"), (self.t("打开本地视频", "Open video"), "file"),
                             (self.t("下载视频", "Download"), "download"), (self.t("切换增强 · F6", "Toggle NR · F6"), "toggle")):
            playback.addWidget(button(text, lambda checked=False, value=action: self.video_action(value)))
        playback.addStretch()
        layout.addLayout(playback)
        layout.addWidget(label(self.t("导出增强视频", "RENDER TO FILE"), "eyebrow"))
        render = row()
        self.video_scale = ComboBox()
        for key, value in video.SCALES.items():
            self.video_scale.addItem(key, key)
        self.video_style = ComboBox()
        for key, value in video.STYLES.items():
            self.video_style.addItem(str(value), key)
        render.addWidget(self.video_scale)
        render.addWidget(self.video_style)
        render.addWidget(button(self.t("选择视频并渲染…", "Choose and render…"), lambda: self.video_action("render")))
        render.addStretch()
        layout.addLayout(render)
        layout.addWidget(label(self.t("摄像头", "CAMERA"), "eyebrow"))
        camera = row()
        self.camera_combo = ComboBox()
        self.camera_combo.setMinimumWidth(180)
        camera.addWidget(self.camera_combo, 1)
        camera.addWidget(button(self.t("刷新", "Refresh"), lambda: self.video_action("cameras")))
        camera.addWidget(button(self.t("开始", "Start"), lambda: self.video_action("camera")))
        camera.addWidget(button(self.t("停止", "Stop"), lambda: self.video_action("stop")))
        layout.addLayout(camera)
        layout.addWidget(label(self.t("屏幕与窗口", "SCREEN AND WINDOW"), "eyebrow"))
        capture = row()
        self.screen_combo = ComboBox()
        capture.addWidget(self.screen_combo, 1)
        capture.addWidget(button(self.t("刷新", "Refresh"), lambda: self.video_action("screens")))
        capture.addWidget(button(self.t("开始", "Start"), lambda: self.video_action("screen")))
        capture.addWidget(button(self.t("停止", "Stop"), lambda: self.video_action("stop")))
        layout.addLayout(capture)
        layout.addWidget(label(self.t("单屏捕获左侧区域，播放器放在右侧；双屏时使用另一屏显示。也可选择单个窗口。摄像头与屏幕捕获不能同时运行。",
            "Single-monitor capture uses the left region; the player sits on the right. With two monitors the player uses the other screen. You can also select a window. Camera and screen capture share one session."), "muted", True))
        layout.addStretch()
        return scroller(page)

    def setup_video(self):
        folder = QFileDialog.getExistingDirectory(self, self.t("选择播放器文件夹", "Choose player folder"))
        if folder:
            self._submit(lambda emit: video.prepare(Path(folder), on_log=lambda text: emit("log", text),
                on_prog=lambda p, text: emit("progress", (p, text))),
                lambda game: self._added(LibraryEntry(game, False)), busy=True,
                title=self.t("正在配置播放器…", "Setting up player…"))

    def video_action(self, action):
        if self.busy_job:
            return
        target = self.video_url.text().strip()
        scale = self.video_scale.currentData()
        style = self.video_style.currentData()
        camera = self.camera_combo.currentText()
        screen = self.screen_combo.currentText()
        if action in ("screen", "camera") and not (screen if action == "screen" else camera):
            self.show_text(self.t("请选择来源", "Select a source"), self.t("先刷新列表，再选择要捕获的来源。", "Refresh the list and select a capture source first."))
            return
        filename = ""
        if action in ("file", "render"):
            filename, _ = QFileDialog.getOpenFileName(self, self.t("选择视频", "Choose video"))
            if not filename:
                return
        if action in ("url", "download") and not target:
            self.video_url.setFocus()
            return
        def work(emit):
            if action == "toggle":
                return video.toggle_nr()
            if action == "stop":
                return video.stop_webcam()
            if action == "screens":
                return video.list_screens()
            game = video.known()
            if not game:
                raise ValueError("请安装播放器 / Set up the player first")
            folder = game.install_dir
            if action == "url":
                return video.play_url(folder, target)
            if action == "file":
                return video.launch(folder, filename)
            if action == "cameras":
                return video.list_cameras(folder)
            if action == "camera":
                return video.start_webcam(folder, camera)
            if action == "screen":
                return video.start_screen(folder, screen)
            callbacks = {"on_log": lambda text: emit("log", text), "on_prog": lambda p, text: emit("progress", (p, text))}
            if action == "download":
                return video.download(folder, target, **callbacks)
            return video.process(folder, Path(filename), scale=scale, style=style, **callbacks)
        def done(result):
            if action == "screens":
                self.screen_combo.clear()
                self.screen_combo.addItems(result)
            elif action == "cameras":
                self.camera_combo.clear()
                self.camera_combo.addItems(result)
            elif isinstance(result, Path):
                self.show_text(self.t("已完成", "Complete"), str(result))
        self._submit(work, done, busy=True, title=self.t("正在处理视频…", "Processing video…"))

    def show_remix(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("RTX Remix")
        dialog.resize(780, 600)
        layout = column(dialog, 24)
        layout.addWidget(label("RTX Remix", "heading"))
        layout.addWidget(label(self.t("先安装对应模组，再扫描游戏库。本工具会识别 Remix 路线。", "Install a game's Remix mod, then rescan. Rescan to detect its runtime."), "muted", True))
        body = QWidget()
        cards = column(body, 0)
        owned = {id(mod): game for game, mod in remixlist.for_library([entry.game for entry in self.model.entries])}
        for mod in list(remixlist.BUILT_IN) + list(remixlist.MODS):
            frame = QFrame()
            frame.setObjectName("card")
            item = column(frame, 14, 6)
            item.addWidget(label(mod.game, "subheading"))
            item.addWidget(label(mod.mod, "muted", True))
            game = owned.get(id(mod))
            if game:
                item.addWidget(label(self.t("已找到本地游戏", "Local game found"), "badge"), alignment=Qt.AlignmentFlag.AlignLeft)
            url = getattr(mod, "url", "")
            if url:
                item.addWidget(button(self.t("打开模组页面 ↗", "Open project ↗"), lambda checked=False, u=url: QDesktopServices.openUrl(QUrl(u)), "ghost"), alignment=Qt.AlignmentFlag.AlignLeft)
            if mod.installable and game:
                item.addWidget(button(self.t("下载并安装模组", "Download and install mod"),
                    lambda checked=False, m=mod, g=game: self.install_remix(dialog, m, g)))
            cards.addWidget(frame)
        layout.addWidget(scroller(body), 1)
        dialog.exec()

    def install_remix(self, dialog, mod, game):
        if self.busy_job:
            return
        dialog.accept()
        def work(emit):
            return remixdl.install(mod.url, game.install_dir, log=lambda text: emit("log", text),
                progress=lambda done, total: emit("progress", (int(done * 100 / total) if total else 0, mod.game)))
        self._submit(work, lambda result: self.show_text(self.t("模组安装完成", "Mod installed"),
            self.t("请重新扫描游戏库，以识别 Remix 路线。", "Rescan the library to detect the Remix route.")),
            busy=True, title=self.t("正在安装 Remix 模组…", "Installing Remix mod…"))
        self.navigate(2)

    def show_comparison(self):
        entry = self.current
        if not entry:
            return
        def done(files):
            pair = compare.pair(files)
            if not pair:
                self.show_text(self.t("未找到对比截图", "No comparison screenshots found"), self.t("在游戏中关闭增强后截图，再按 F6 开启增强并截图。两张 PNG 截图需要在几分钟内拍摄，然后重新打开对比。", "Take a PNG with neural rendering off, toggle F6, then take another within a few minutes. Reopen this comparison."))
                return
            dialog = QDialog(self)
            dialog.setWindowTitle(self.t("效果对比", "Before / after"))
            dialog.resize(1000, 620)
            layout = row(dialog)
            for title, filename in zip((self.t("关闭 DLSS 5", "DLSS 5 off"), self.t("开启 DLSS 5", "DLSS 5 on")), pair):
                pane = QWidget()
                content = column(pane, 16)
                content.addWidget(label(title, "subheading"))
                image = QLabel()
                image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                pixmap = QPixmap(str(filename))
                image.setPixmap(pixmap.scaled(QSize(700, 460), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                content.addWidget(scroller(image), 1)
                content.addWidget(label(filename.name, "muted", True))
                layout.addWidget(pane)
            dialog.exec()
        self._submit(lambda emit: compare.find_screenshots(entry.game.install_dir), done)

    def closeEvent(self, event):
        if self.jobs.active:
            self.status.setText(self.t("任务正在运行，完成后可关闭。", "A task is running. Close after it finishes."))
            event.ignore()
            return
        prefs.set_("studio_window", [self.width(), self.height()])
        prefs.set_("studio_window_layout", 1)
        self.jobs.shutdown()
        video.stop_webcam()
        event.accept()


def run():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("JustDLSS5.Desktop")
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName(NAME)
    app.setApplicationVersion(VERSION)
    app.setFont(QFont("Microsoft YaHei UI", 10))
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    return app.exec()
