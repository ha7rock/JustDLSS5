"""Shared desktop controls with consistent popup geometry."""
from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QListView,
    QPushButton, QSlider, QStyledItemDelegate, QStyle, QStyleOptionButton,
    QStyleOptionComboBox, QStylePainter, QToolTip)


class Button(QPushButton):
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
