"""Shared desktop controls with consistent popup geometry."""
from html import escape
from PySide6.QtCore import QPoint, QRect, QRectF, QSize, Qt, QTimer, QEvent
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QListView,
    QPushButton, QSlider, QStyledItemDelegate, QStyle, QStyleOptionButton,
    QStyleOptionComboBox, QStylePainter, QToolTip, QToolButton, QWidget, QLabel, QVBoxLayout)


class HelpPopup(QWidget):
    """Non-activating help card with transparent, antialiased corners."""

    def __init__(self, owner, text):
        super().__init__(owner, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.body = QLabel(self)
        self.body.setWordWrap(True)
        self.body.setText('<p style="line-height:145%; margin:0">' + escape(text) + '</p>')
        self.body.setStyleSheet("color: #e4e8ee; background: transparent; border: none; font-size: 14px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.addWidget(self.body)

    def show_at(self, owner):
        area = owner.screen().availableGeometry().adjusted(8, 8, -8, -8)
        width = min(340, area.width())
        self.body.setFixedWidth(width - 36)
        height = self.body.heightForWidth(width - 36) + 32
        self.setFixedSize(width, height)
        point = owner.mapToGlobal(QPoint(0, owner.height() + 8))
        if point.y() + height > area.bottom():
            point.setY(owner.mapToGlobal(QPoint(0, -height - 8)).y())
        point.setX(max(area.left(), min(point.x(), area.right() - width + 1)))
        point.setY(max(area.top(), min(point.y(), area.bottom() - height + 1)))
        self.move(point)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#454e5a"), 1))
        painter.setBrush(QColor("#272e37"))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(.5, .5, -.5, -.5), 12, 12)


class HelpButton(QToolButton):
    """Show help after 750 ms of hover; leaving cancels it."""

    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.setObjectName("contextHelp")
        self.setText("?")
        self.setFixedSize(16, 16)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAccessibleName(title)
        self.setAccessibleDescription(text)
        self._popup = None
        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._hover_timer.setInterval(750)
        self._hover_timer.timeout.connect(self._show_help)

    def enterEvent(self, event):
        super().enterEvent(event)
        self._hover_timer.start()

    def leaveEvent(self, event):
        self._dismiss()
        super().leaveEvent(event)

    def hideEvent(self, event):
        self._dismiss()
        super().hideEvent(event)

    def event(self, event):
        if event.type() == QEvent.Type.ToolTip:
            return True
        return super().event(event)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.ApplicationDeactivate or (
                event.type() == QEvent.Type.WindowDeactivate and watched is self.window()):
            self._dismiss()
        return False

    def _show_help(self):
        if not self.isVisible() or not self.isEnabled() or not self.underMouse():
            return
        if self._popup is None:
            self._popup = HelpPopup(self, self.accessibleDescription())
        QApplication.instance().installEventFilter(self)
        self._popup.show_at(self)

    def _dismiss(self):
        QApplication.instance().removeEventFilter(self)
        self._hover_timer.stop()
        if self._popup is not None:
            self._popup.hide()


class Button(QPushButton):
    def set_loading(self, loading):
        if loading:
            if getattr(self, "_loading_timer", None):
                return
            self._idle_icon = self.icon()
            self._angle = 0
            self._loading_timer = QTimer(self)
            self._loading_timer.setInterval(40)
            self._loading_timer.timeout.connect(self._spin)
            self._spin()
            self._loading_timer.start()
        elif getattr(self, "_loading_timer", None):
            self._loading_timer.stop()
            self._loading_timer.deleteLater()
            self._loading_timer = None
            self.setIcon(self._idle_icon)

    def _spin(self):
        ratio = self.devicePixelRatioF()
        pixmap = QPixmap(round(18 * ratio), round(18 * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#b6e477"), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(3, 3, 12, 12, -self._angle * 16, 260 * 16)
        painter.end()
        icon = QIcon()
        icon.addPixmap(pixmap, QIcon.Mode.Normal)
        icon.addPixmap(pixmap, QIcon.Mode.Disabled)
        self.setIcon(icon)
        self._angle = (self._angle + 16) % 360

    def minimumSizeHint(self):
        hint = super().minimumSizeHint()
        return QSize(min(90, hint.width()), hint.height())

    def paintEvent(self, event):
        option = QStyleOptionButton()
        self.initStyleOption(option)
        area = self.style().subElementRect(QStyle.SubElement.SE_PushButtonContents, option, self)
        width = area.width() - (option.iconSize.width() + 6 if not option.icon.isNull() else 0)
        option.text = self.fontMetrics().elidedText(self.text(), Qt.TextElideMode.ElideRight, max(0, width))
        painter = QStylePainter(self)
        painter.drawControl(QStyle.ControlElement.CE_PushButton, option)


class OptionDelegate(QStyledItemDelegate):
    def helpEvent(self, event, view, option, index):
        if event.type() == event.Type.ToolTip and index.isValid():
            QToolTip.showText(event.globalPos(), str(index.data() or ""), view)
            return True
        return super().helpEvent(event, view, option, index)


class Slider(QSlider):
    def wheelEvent(self, event):
        # Leave the value alone and let the surrounding scroll area handle it.
        event.ignore()


class ComboBox(QComboBox):
    def wheelEvent(self, event):
        # Scrolling the page must not change a closed field. The popup's view
        # handles its own wheel events when the user opens the options.
        event.ignore()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(8)
        self.currentTextChanged.connect(self.setToolTip)
        # Qt's combo animation captures the native popup before our placement,
        # making it animate from the wrong rectangle and delaying interaction.
        QApplication.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)
        self.setView(QListView())
        self.view().setItemDelegate(OptionDelegate(self.view()))
        self.view().setMouseTracking(True)
        self.view().viewport().setMouseTracking(True)
        self.view().setUniformItemSizes(True)
        # One antialiased border on an alpha surface. A polygon window mask
        # quantizes the same curve a second time and damages its top corners.
        popup = self.view().window()
        popup.setObjectName("comboPopup")
        # Windows requires a frameless top-level window for per-pixel alpha;
        # WA_TranslucentBackground alone leaves a black native backing surface.
        popup.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        popup.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint, True)
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        popup.setAutoFillBackground(False)
        popup.setFrameShape(QFrame.Shape.NoFrame)
        popup.setStyleSheet("QFrame#comboPopup { background: transparent; border: none; }")
        self.setMaxVisibleItems(10)
        self.view().setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view().setTextElideMode(Qt.TextElideMode.ElideRight)

    def paintEvent(self, event):
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        area = self.style().subControlRect(QStyle.ComplexControl.CC_ComboBox, option,
                                          QStyle.SubControl.SC_ComboBoxEditField, self)
        option.currentText = self.fontMetrics().elidedText(option.currentText,
            Qt.TextElideMode.ElideRight, max(0, area.width() - 4))
        painter = QStylePainter(self)
        painter.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, option)
        painter.drawControl(QStyle.ControlElement.CE_ComboBoxLabel, option)

    def showPopup(self):
        if not self.count():
            return
        super().showPopup()
        popup = self.view().window()
        screen = self.screen().availableGeometry()
        below = self.mapToGlobal(QPoint(0, self.height() + 4))
        row_height = max(28, self.view().sizeHintForRow(0))
        height = row_height * min(self.count(), self.maxVisibleItems()) + 10
        space = screen.bottom() - below.y() + 1
        # Prefer below, scrolling long lists; flip only at the screen edge.
        y = below.y()
        if space >= row_height + 10:
            height = min(height, space)
        else:
            bottom = self.mapToGlobal(QPoint(0, -4)).y()
            height = min(height, bottom - screen.top())
            y = bottom - height
        width = min(self.width(), screen.width())
        x = max(screen.left(), min(below.x(), screen.right() - width + 1))
        popup.setGeometry(QRect(x, y, width, height))
        self.view().scrollTo(self.view().currentIndex())
