"""Memory-only Qt model. Painting, filtering and resizing never touch disk."""
from .icons import usable_image
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel, QSize, QRectF
from PySide6.QtGui import QColor, QIcon, QPixmap, QPalette, QPainter, QPainterPath, QFont
from PySide6.QtWidgets import QTableView, QStyledItemDelegate, QStyle, QApplication, QListView


class LibraryModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries = []
        self.chinese = True
        self.icons = {}
        self.covers = {}
        self.metadata = {}

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
        self.status = 0
        self.source = ""
        self.order = "name"
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def set_query(self, query, installed=False, arch=0, status=0, source=""):
        self.beginFilterChange()
        self.terms = query.casefold().split()
        self.only_installed = installed
        self.arch = arch
        self.status = status
        self.source = source
        self.endFilterChange(QSortFilterProxyModel.Direction.Rows)

    def filterAcceptsRow(self, row, parent):
        entry = self.sourceModel().entries[row]
        game = entry.game
        haystack = f"{game.name} {game.source} {game.folder}".casefold()
        return (all(term in haystack for term in self.terms)
                and (not self.only_installed or entry.installed)
                and (not self.arch or game.bitness in (None, self.arch))
                and (not self.source or game.source == self.source)
                and (self.status != 2 or not entry.installed)
                and (self.status != 3 or bool(entry.anticheat or game.error))
                and (self.status != 4 or self.sourceModel().metadata.get(entry.key, {}).get("favorite", False)))


    def lessThan(self, left, right):
        model = self.sourceModel()
        a, b = model.entries[left.row()], model.entries[right.row()]
        ma, mb = model.metadata.get(a.key, {}), model.metadata.get(b.key, {})
        def key(entry, meta):
            favorite = not meta.get("favorite", False)
            if self.order == "added":
                value = -meta.get("added", 0)
            elif self.order == "recent":
                value = -meta.get("recent", 0)
            elif self.order == "source":
                value = entry.game.source.casefold()
            else:
                value = entry.game.name.casefold()
            return favorite, value, entry.game.name.casefold(), entry.key
        return key(a, ma) < key(b, mb)


class CoverDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        return self.parent().gridSize()

    def paint(self, painter, option, index):
        entry = index.data(Qt.ItemDataRole.UserRole)
        if not entry:
            return
        model = index.model().sourceModel()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = option.rect.adjusted(5, 5, -5, -5)
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hover = bool(option.state & QStyle.StateFlag.State_MouseOver)
        painter.setPen(QColor("#b6e477" if selected else "#64764c" if hover else "#323b47"))
        painter.setBrush(QColor("#2b3529" if selected else "#29313b" if hover else "#20262f"))
        painter.drawRoundedRect(QRectF(rect), 10, 10)
        art = rect.adjusted(8, 8, -8, -70)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(art), 6, 6)
        painter.save()
        painter.setClipPath(clip)
        painter.fillRect(art, QColor("#151b23"))
        cover = model.covers.get(entry.key)
        if cover and not cover.isNull():
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            # Preserve the complete cover; never stretch or crop its title.
            fitted = cover.size().scaled(art.size(), Qt.AspectRatioMode.KeepAspectRatio)
            dest = art.adjusted(0, 0, 0, 0)
            dest.setSize(fitted)
            dest.moveCenter(art.center())
            painter.drawPixmap(dest, cover)
        else:
            icon = model.icons.get(entry.key)
            if icon:
                icon.paint(painter, art.center().x()-24, art.center().y()-24, 48, 48)
        painter.restore()
        favorite = model.metadata.get(entry.key, {}).get("favorite", False)
        title = ("★ " if favorite else "") + entry.game.name
        font = QFont(option.font)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#f1a7a2" if entry.anticheat else "#e5e9ef"))
        title_rect = rect.adjusted(10, rect.height()-65, -10, -40)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignVCenter,
                         painter.fontMetrics().elidedText(title, Qt.TextElideMode.ElideRight, title_rect.width()))
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor("#9ba8b7"))
        source_rect = rect.adjusted(10, rect.height()-41, -10, -22)
        painter.drawText(source_rect, Qt.AlignmentFlag.AlignVCenter, entry.game.source)
        zh = model.chinese
        status = ("已安装增强" if zh else "Components installed") if entry.installed else ("未安装增强" if zh else "No components")
        if entry.anticheat:
            status = "反作弊风险" if zh else "Anti-cheat risk"
        elif entry.game.error:
            status = "需要检查" if zh else "Needs attention"
        painter.setPen(QColor("#f1a7a2" if entry.anticheat or entry.game.error else "#b6e477" if entry.installed else "#9ba8b7"))
        status_rect = rect.adjusted(10, rect.height()-22, -10, -4)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignVCenter,
                         painter.fontMetrics().elidedText(status, Qt.TextElideMode.ElideRight, status_rect.width()))
        painter.restore()


class CoverView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setMovement(QListView.Movement.Static)
        self.setWrapping(True)
        self.setUniformItemSizes(True)
        self.setLayoutMode(QListView.LayoutMode.Batched)
        self.setBatchSize(60)
        self.setMouseTracking(True)
        self.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        self.setItemDelegate(CoverDelegate(self))
        self.setGridSize(QSize(172, 276))
        self.setStyleSheet("QListView { background: transparent; border: none; }")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = max(1, self.viewport().width())
        columns = max(1, width // 172)
        self.setGridSize(QSize(max(1, width // columns), 276))


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
