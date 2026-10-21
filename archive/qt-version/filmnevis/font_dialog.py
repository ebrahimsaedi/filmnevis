"""دیالوگ انتخاب فونت سفارشی — با جستجو و پیش‌نمایش."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class FontPickerDialog(QDialog):
    """دیالوگ انتخاب فونت با جستجو و پیش‌نمایش."""

    def __init__(self, current_family: str, current_size: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("انتخاب فونت")
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(560, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # ── جستجو ──
        self.search = QLineEdit()
        self.search.setPlaceholderText("جستجوی فونت...")
        self.search.textChanged.connect(self._filter_fonts)
        layout.addWidget(self.search)

        # ── لیست فونت‌ها ──
        self.font_list = QListWidget()
        self.font_list.setLayoutDirection(Qt.LeftToRight)
        families = QFontDatabase.families()
        for fam in families:
            item = QListWidgetItem(fam)
            item.setData(Qt.UserRole, fam)
            self.font_list.addItem(item)
        self.font_list.currentItemChanged.connect(self._on_font_changed)
        layout.addWidget(self.font_list, 1)

        # ── اندازه ──
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("اندازه (پوینت):"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(current_size)
        self.size_spin.valueChanged.connect(self._update_preview)
        size_row.addWidget(self.size_spin)
        size_row.addStretch()
        layout.addLayout(size_row)

        # ── پیش‌نمایش ──
        self.preview = QLabel("نمونه متن فارسی — این یک تست است")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(90)
        self.preview.setStyleSheet(
            "background-color: #ffffff; color: #000000;"
            "border: 1px solid #c8c8c8; border-radius: 4px; padding: 12px;"
        )
        layout.addWidget(self.preview)

        # ── دکمه‌ها ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton("تأیید")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        # مقدار اولیه
        self._select_font(current_family)
        self._update_preview()

    def _select_font(self, family: str):
        for i in range(self.font_list.count()):
            item = self.font_list.item(i)
            if item.data(Qt.UserRole) == family:
                self.font_list.setCurrentItem(item)
                self.font_list.scrollToItem(item)
                return

    def _filter_fonts(self, text: str):
        needle = text.strip().lower()
        for i in range(self.font_list.count()):
            item = self.font_list.item(i)
            fam = item.data(Qt.UserRole) or ""
            item.setHidden(bool(needle) and needle not in fam.lower())

    def _on_font_changed(self, _cur, _prev=None):
        self._update_preview()

    def _update_preview(self):
        family = self.selected_family()
        size = self.size_spin.value()
        font = QFont(family)
        font.setPointSize(size)
        self.preview.setFont(font)
        self.preview.setText(f"نمونه متن فارسی — {family}")

    def selected_family(self) -> str:
        item = self.font_list.currentItem()
        if item is None:
            return ""
        return item.data(Qt.UserRole) or ""

    def selected_size(self) -> int:
        return self.size_spin.value()
