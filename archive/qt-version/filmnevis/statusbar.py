"""نوارهای وضعیت پایین — دو نوار شناور."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

from filmnevis.widgets import Stepper


def to_persian_digits(value) -> str:
    s = f"{value:,}".replace(",", "٬")
    trans = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return s.translate(trans)


class CountersBar(QWidget):
    """نوار شناور — همه‌ی آمار."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusbar")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 8, 18, 8)
        layout.setSpacing(18)

        self.lbl_words = QLabel("کلمات: ۰")
        self.lbl_scenes = QLabel("صحنه: ۰")
        self.lbl_chars = QLabel("شخصیت: ۰")
        self.lbl_page = QLabel("صفحه: ۱ از ۱")
        self.lbl_duration = QLabel("~۰ دقیقه")

        for lbl in (self.lbl_words, self.lbl_scenes, self.lbl_chars,
                    self.lbl_page, self.lbl_duration):
            lbl.setObjectName("statusLabel")
            layout.addWidget(lbl)

    def set_stats(self, words: int, scenes: int, chars: int,
                  current_page: int, total_pages: int, duration_min: int):
        self.lbl_words.setText(f"کلمات: {to_persian_digits(words)}")
        self.lbl_scenes.setText(f"صحنه: {to_persian_digits(scenes)}")
        self.lbl_chars.setText(f"شخصیت: {to_persian_digits(chars)}")
        self.lbl_page.setText(
            f"صفحه: {to_persian_digits(current_page)} از "
            f"{to_persian_digits(total_pages)}"
        )
        self.lbl_duration.setText(f"~{to_persian_digits(duration_min)} دقیقه")

    # سازگاری
    def set_word_count(self, n): pass
    def set_page(self, current, total): pass
    def set_char_count(self, n): pass
    def set_element(self, label): pass
    def set_zoom(self, percent): pass
    def set_icon_color(self, color): pass


class ZoomBar(QWidget):
    """نوار شناور — کنترل زوم با آیکون‌های ذره‌بین.

    کلیک روی عدد زوم → بازگشت به ۱۰۰٪.
    """

    zoom_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusbar")
        self.setLayoutDirection(Qt.LeftToRight)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(0)

        # ★ کلیک روی عدد → بازگشت به ۱۰۰٪
        self.stepper = Stepper(
            min_val=25, max_val=300, step=10, value=100,
            suffix="٪",
            icon_minus="zoom-out",
            icon_plus="zoom-in",
            icon_color="#1A1A1A",
            spin_width=54, icon_size=17, btn_size=26, spin_height=28,
            click_resets_to=100,
        )
        self.stepper.setToolTip("زوم — کلیک روی عدد، بازگشت به ۱۰۰٪")
        self.stepper.value_changed.connect(self.zoom_changed.emit)
        layout.addWidget(self.stepper)

    def set_zoom(self, percent: int):
        self.stepper.set_value(percent)

    def set_icon_color(self, color: str):
        self.stepper.set_icon_color(color)

    def zoom_in(self):
        self.stepper.set_value(self.stepper.value() + 10)

    def zoom_out(self):
        self.stepper.set_value(self.stepper.value() - 10)

    # سازگاری
    def set_char_count(self, n): pass
    def set_element(self, label): pass
    def set_word_count(self, n): pass
    def set_page(self, current, total): pass


class FilmnevisStatusBar(CountersBar):
    pass
