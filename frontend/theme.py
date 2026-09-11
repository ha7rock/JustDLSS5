from pathlib import Path
"""Desktop design tokens. Logical pixels are scaled once by Qt, not Python."""
BG = "#101215"
PANEL = "#191c21"
TEXT = "#f0f2f5"
MUTED = "#929aa6"
ACCENT = "#b6e477"

STYLES = """
QWidget { color: #e7eaf0; font-family: 'Segoe UI', 'Microsoft YaHei UI'; font-size: 13px; }
QMainWindow, QDialog { background: #101215; }
QWidget#sidebar { background: #14171b; border-right: 1px solid #292d34; }
QWidget#detail, QFrame#card { background: #191c21; border: 1px solid #30353e; border-radius: 12px; }
QLabel { background: transparent; border: none; }
QLabel#heading { font-size: 29px; font-weight: 650; letter-spacing: -0.6px; color: #f7f9fc; }
QLabel#subheading { font-size: 18px; font-weight: 600; color: #f1f3f6; }
QLabel#muted { color: #929aa6; font-size: 12px; }
QLabel#eyebrow { color: #8b949f; font-size: 10px; font-weight: 600; letter-spacing: 1.4px; }
QLabel#badge { background: #293526; color: #b6e477; border-radius: 5px; padding: 4px 8px; font-size: 11px; }
QLabel#warning { color: #f1a7a2; background: #382225; padding: 10px; border-radius: 6px; }
QLabel#notice { background: #27251d; color: #d9c596; border: 1px solid #46402d; border-radius: 8px; padding: 10px; font-size: 12px; }
QPushButton { background: #242930; border: 1px solid #363e48; border-radius: 7px; padding: 9px 14px; font-weight: 500; }
QPushButton:hover { background: #303741; border-color: #596472; }
QPushButton:pressed { background: #1b2027; }
QPushButton:disabled { color: #626b77; background: #1e2228; border-color: #2d323a; }
QPushButton#primary { background: #b6e477; color: #16230c; border-color: #b6e477; font-weight: 650; }
QPushButton#primary:hover { background: #c7ef95; }
QPushButton#primary:disabled { background: #303b28; color: #758766; border-color: #303b28; }
QPushButton#nav { background: transparent; border: none; padding: 12px 16px; text-align: left; color: #9da6b2; }
QPushButton#nav:hover { background: #20252c; color: #ffffff; }
QPushButton#nav:checked { background: #2a3425; color: #c7eca1; }
QPushButton#ghost { background: transparent; border-color: transparent; color: #a6afb9; }
QPushButton#ghost:hover { background: #242930; color: #ffffff; }
QPushButton#danger { color: #f1a7a2; }
QLineEdit, QComboBox, QSpinBox { background: #16191e; border: 1px solid #343b45; border-radius: 7px; padding: 8px 10px; selection-background-color: #415634; }
QLineEdit:focus, QComboBox:focus { border-color: #9cbf70; }
QComboBox { combobox-popup: 0; }
QComboBox::down-arrow { image: url("__CHEVRON__"); width: 12px; height: 12px; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView { background: #16191e; border: 1px solid #343b45; border-radius: 7px; selection-background-color: #36442e; padding: 4px; outline: none; }
QComboBox QAbstractItemView::item { min-height: 28px; padding: 2px 8px; border-radius: 4px; }
QComboBox QAbstractItemView::item:hover { background: #303d2a; color: #e0f2ca; }
QComboBox QAbstractItemView::item:selected { background: #36442e; color: #c7eca1; }
QComboBox QAbstractItemView::item:selected:hover { background: #455738; color: #effcdd; }
QTableView { background: transparent; alternate-background-color: #171b20; border: none; gridline-color: transparent; selection-background-color: #293627; outline: none; }
QTableView::item { border-bottom: 1px solid #252a32; padding: 10px; }
QTableView::item:selected { background: #293627; }
QTableView::item:hover { background: #22282e; }
QHeaderView::section { background: #101215; color: #89939f; border: none; border-bottom: 1px solid #303640; padding: 12px 10px; font-size: 11px; text-align: left; }
QScrollArea { background: transparent; border: none; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 3px 0; }
QScrollBar::handle:vertical { background: #414952; border-radius: 4px; min-height: 28px; }
QScrollBar:horizontal { background: transparent; height: 8px; }
QScrollBar::handle:horizontal { background: #414952; border-radius: 4px; min-width: 28px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
QSplitter::handle { background: transparent; }
QSplitter::handle:hover { background: #4b5940; }
QPlainTextEdit { background: #14171b; border: 1px solid #303640; border-radius: 8px; padding: 12px; font-family: 'Cascadia Mono', 'Consolas'; font-size: 12px; }
QTabWidget::pane { border: none; }
QTabBar::tab { background: #191c21; color: #929aa6; padding: 10px 18px; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #c7eca1; border-bottom-color: #b6e477; }
QTabBar::tab:hover { background: #242930; }
QProgressBar { background: #292f37; border: none; border-radius: 2px; height: 4px; }
QProgressBar::chunk { background: #b6e477; border-radius: 2px; }
QSlider::groove:horizontal { background: #363e47; height: 4px; border-radius: 2px; }
QSlider::sub-page:horizontal { background: #b6e477; border-radius: 2px; }
QSlider::handle:horizontal { background: #c5eba0; width: 14px; margin: -5px 0; border-radius: 7px; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 15px; height: 15px; }
QCheckBox::indicator:unchecked { background: #14171b; border: 1px solid #657080; border-radius: 3px; }
QCheckBox::indicator:checked { background: #14171b; border: 1px solid #b6e477; border-radius: 3px; image: url("__CHECK__"); }
QCheckBox::indicator:hover { border-color: #c7eca1; }
QCheckBox::indicator:disabled { border-color: #454d57; background: #1b1e23; }
QToolButton { color: #b7c0cd; border: none; padding: 10px 0; text-align: left; }
QMenu { background: #20252c; border: 1px solid #3c4551; padding: 6px; }
QMenu::item { padding: 8px 18px; border-radius: 4px; }
QMenu::item:selected { background: #37432e; }
QToolTip { background: #303741; color: #f0f2f5; border: 1px solid #596472; padding: 6px; }
"""

STYLES = STYLES.replace("__CHEVRON__", (Path(__file__).parent / "chevron.svg").as_posix())
STYLES = STYLES.replace("__CHECK__", (Path(__file__).parent / "check.svg").as_posix())
