"""Memory-only Qt model. Painting, filtering and resizing never touch disk."""
from .icons import usable_image
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel
from PySide6.QtGui import QColor, QIcon, QPixmap, QPalette
from PySide6.QtWidgets import QTableView, QStyledItemDelegate, QStyle, QApplication


class LibraryModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries = []
        self.chinese = True
        self.icons = {}

    def replace(self, entries):
        self.beginResetModel()
        self.entries = list(entries)
        fallback = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.icons = {e.key: QIcon(QPixmap.fromImage(e.icon_image)) if usable_image(e.icon_image) else fallback for e in self.entries}
        self.endResetModel()

    def refresh(self):
        if self.entries:
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.entries)-1, 3))

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        return 4

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return (("游戏", "来源", "图形接口", "状态") if self.chinese else
                    ("GAME", "SOURCE", "GRAPHICS", "STATUS"))[section]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        entry = self.entries[index.row()]
        game = entry.game
        if role == Qt.ItemDataRole.DecorationRole and index.column() == 0:
            return self.icons.get(entry.key)
        if role == Qt.ItemDataRole.UserRole:
            return entry
        if role == Qt.ItemDataRole.ToolTipRole:
            return f"{game.name}\n{game.folder}\n{game.api} · {game.bitness or '?'} bit"
        if role == Qt.ItemDataRole.ForegroundRole:
            return QColor("#f1a7a2" if entry.anticheat else "#b6e477" if index.column() == 3 and entry.installed else
                          "#e5e9ef" if index.column() == 0 else "#929ca9")
        if role == Qt.ItemDataRole.DisplayRole:
            status = ("已安装" if self.chinese else "Installed") if entry.installed else (
                "未安装" if self.chinese else "Not installed")
            if entry.anticheat:
                status = "⚠ " + entry.anticheat
            return (game.name, game.source, f"{game.api} · {game.bitness or '?'} bit", status)[index.column()]


class LibraryFilter(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.terms = []
        self.only_installed = False
        self.arch = 0
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def set_query(self, query, installed=False, arch=0):
        self.beginFilterChange()
        self.terms = query.casefold().split()
        self.only_installed = installed
        self.arch = arch
        self.endFilterChange(QSortFilterProxyModel.Direction.Rows)

    def filterAcceptsRow(self, row, parent):
        entry = self.sourceModel().entries[row]
        game = entry.game
        haystack = f"{game.name} {game.source} {game.folder}".casefold()
        return (all(term in haystack for term in self.terms)
                and (not self.only_installed or entry.installed)
                and (not self.arch or game.bitness in (None, self.arch)))


class RowDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.row() == self.parent().hover_row:
            option.state |= QStyle.StateFlag.State_MouseOver
        else:
            option.state &= ~QStyle.StateFlag.State_MouseOver
        entry = index.data(Qt.ItemDataRole.UserRole)
        option.palette.setColor(QPalette.ColorRole.HighlightedText,
                                QColor("#f1a7a2" if entry and entry.anticheat else "#dcf1c5"))
        super().paint(painter, option, index)


class LibraryTable(QTableView):
    def __init__(self):
        super().__init__()
        self.hover_row = -1
        self.setMouseTracking(True)
        self.setItemDelegate(RowDelegate(self))

    def mouseMoveEvent(self, event):
        row = self.indexAt(event.position().toPoint()).row()
        if row != self.hover_row:
            self.hover_row = row
            self.viewport().update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hover_row = -1
        self.viewport().update()
        super().leaveEvent(event)
