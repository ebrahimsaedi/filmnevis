"""ویجت‌های قابل استفاده‌ی مجدد."""

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QBoxLayout,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from filmnevis.icons import get_icon


class Stepper(QWidget):
    """کنترل عددی: [−آیکون] [عدد داخل کپسول] [+آیکون]

    - پس‌زمینه شفاف (بدون کادر بیرونی)
    - آیکون‌های + و − از SVG
    - عدد داخل یک کپسول کوچک
    - محتوا وسط‌چین در عرض کل

    اگر click_resets_to داده شود:
        کلیک روی عدد → مقدار به اون عدد برمی‌گرده (ویرایش غیرفعال).
    در غیر این صورت:
        عدد قابل ویرایش است.
    """

    value_changed = Signal(int)

    def __init__(self, min_val=0, max_val=100, step=1, value=0,
                 suffix="", icon_minus="minus", icon_plus="plus",
                 icon_color="#1A1A1A", spin_width=54,
                 icon_size=16, btn_size=26, spin_height=28,
                 click_resets_to=None, parent=None):
        super().__init__(parent)
        self.setObjectName("stepper")
        self.setLayoutDirection(Qt.LeftToRight)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._step = step
        self._icon_minus_name = icon_minus
        self._icon_plus_name = icon_plus
        self._icon_color = icon_color
        self._icon_size = icon_size
        self._btn_size = btn_size
        self._click_resets_to = click_resets_to

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setDirection(QBoxLayout.Direction.LeftToRight)

        # کش‌دار در ابتدا و انتها → محتوا وسط‌چین
        layout.addStretch(1)

        self.btn_minus = QPushButton()
        self.btn_minus.setObjectName("stepperIconBtn")
        self.btn_minus.setCursor(Qt.PointingHandCursor)
        self.btn_minus.setFixedSize(btn_size, btn_size)
        self.btn_minus.clicked.connect(self._on_minus)
        layout.addWidget(self.btn_minus)

        self.spin = QSpinBox()
        self.spin.setObjectName("stepperSpin")
        self.spin.setRange(min_val, max_val)
        self.spin.setSingleStep(step)
        self.spin.setValue(value)
        self.spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin.setSuffix(suffix)
        self.spin.setFixedHeight(spin_height)
        self.spin.setFixedWidth(spin_width)
        self.spin.valueChanged.connect(self.value_changed.emit)
        layout.addWidget(self.spin)

        self.btn_plus = QPushButton()
        self.btn_plus.setObjectName("stepperIconBtn")
        self.btn_plus.setCursor(Qt.PointingHandCursor)
        self.btn_plus.setFixedSize(btn_size, btn_size)
        self.btn_plus.clicked.connect(self._on_plus)
        layout.addWidget(self.btn_plus)

        layout.addStretch(1)

        # ★ حالت کلیک-ریست
        if click_resets_to is not None:
            self.spin.setReadOnly(True)
            self.spin.setCursor(Qt.PointingHandCursor)
            # ★ کلیک روی ناحیه‌ی متن اسپین‌باکس رو هم بگیریم
            #   (چون QSpinBox داخلش QLineEdit داره که موس رو می‌گیره)
            self.spin.installEventFilter(self)
            self.spin.lineEdit().installEventFilter(self)
        else:
            self.spin.setCursor(Qt.IBeamCursor)

        self._apply_icons()

    def eventFilter(self, obj, event):
        """کلیک روی عدد → ریست به مقدار پیش‌فرض (اگه تعریف شده)."""
        if self._click_resets_to is not None:
            if obj is self.spin or obj is self.spin.lineEdit():
                if event.type() == QEvent.Type.MouseButtonPress:
                    self.spin.setValue(self._click_resets_to)
                    return True
        return super().eventFilter(obj, event)

    def _apply_icons(self):
        icon_minus = get_icon(self._icon_minus_name,
                              self._icon_color, self._icon_size)
        icon_plus = get_icon(self._icon_plus_name,
                             self._icon_color, self._icon_size)
        self.btn_minus.setIcon(icon_minus)
        self.btn_minus.setIconSize(QSize(self._icon_size, self._icon_size))
        self.btn_plus.setIcon(icon_plus)
        self.btn_plus.setIconSize(QSize(self._icon_size, self._icon_size))

    def set_icon_color(self, color: str):
        if color == self._icon_color:
            return
        self._icon_color = color
        self._apply_icons()

    def _on_minus(self):
        self.spin.setValue(self.spin.value() - self._step)

    def _on_plus(self):
        self.spin.setValue(self.spin.value() + self._step)

    def value(self) -> int:
        return self.spin.value()

    def set_value(self, v: int):
        self.spin.blockSignals(True)
        self.spin.setValue(v)
        self.spin.blockSignals(False)


class ShadowWrapper(QWidget):
    """ظرف شفاف با سایه/glow — نگه‌داشتن child با پدینگ کافی."""

    def __init__(self, child: QWidget, pad: int = 18,
                 blur: int = 26,
                 color: QColor = None,
                 offset_y: int = 2,
                 parent: QWidget = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(pad, pad, pad, pad)
        lay.setSpacing(0)
        lay.addWidget(child)

        if color is None:
            color = QColor(0, 0, 0, 90)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(blur)
        self._shadow.setColor(color)
        self._shadow.setOffset(0, offset_y)
        self.setGraphicsEffect(self._shadow)

    def set_shadow_color(self, color: QColor):
        self._shadow.setColor(color)

    def set_shadow_offset(self, offset_y: int):
        self._shadow.setOffset(0, offset_y)


def make_shadow_wrapper(child: QWidget, pad: int = 18,
                        blur: int = 26, offset_y: int = 2,
                        color: QColor = None,
                        parent: QWidget = None) -> ShadowWrapper:
    return ShadowWrapper(child, pad=pad, blur=blur,
                         color=color, offset_y=offset_y, parent=parent)
