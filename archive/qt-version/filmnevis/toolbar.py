"""نوار ابزار بالای پنجره — سه بخش، با آیکون‌های SVG."""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QFontDatabase
from PySide6.QtWidgets import (
    QBoxLayout,
    QButtonGroup,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from filmnevis.constants import ELEMENTS
from filmnevis.icons import get_icon, _SIZE_OVERRIDE
from filmnevis.widgets import Stepper


# ═══ ابعاد ثابت ═══
ROW_H = 34
ROW_GAP = 6
BTN_W = 88
FONT_COMBO_W = 170
STEPPER_W = 146
FORMAT_BTN_W = 44
FORMAT_BTN_GAP = 3
TOOL_BTN = 34
TOOL_GAP = 6
SEP_W = 25
SEP_H = 48

# ★ ابعاد کپسول راست — هم‌ترازی افقی ردیف بالا و پایین
#   دو دکمه با عرض ثابت + gap + padding داخلی
CAPSULE_PAD = 4
CAPSULE_W = TOOL_BTN * 2 + TOOL_GAP + CAPSULE_PAD * 2   # 82

# ★ دکمه‌های ردیف بالای پنل راست، پهن‌تر از پایین (طبق درخواست کاربر)
TOP_BTN_W = 36           # 36 × 2 + 6 + 2×2 = 82
TOP_ROW_PAD = 2          # padding کمتر تا دکمه‌ها پهن‌تر شن

TEXT_SECTION_W = FONT_COMBO_W + 10 + STEPPER_W   # 326

ELEM_ROW1 = ["scene", "action", "character"]
ELEM_ROW2 = ["parenthetical", "dialogue", "transition"]


class FilmnevisToolbar(QWidget):
    """نوار ابزار — ۳ بخش."""

    element_selected = Signal(str)
    undo_requested = Signal()
    redo_requested = Signal()
    search_requested = Signal()
    save_requested = Signal()
    save_as_requested = Signal()
    open_requested = Signal()
    new_window_requested = Signal()
    print_requested = Signal()
    export_requested = Signal()
    sidebar_toggled = Signal(bool)
    notes_toggled = Signal(bool)
    font_family_changed = Signal(str)
    font_size_changed = Signal(int)
    bold_toggled = Signal(bool)
    italic_toggled = Signal(bool)
    underline_toggled = Signal(bool)
    color_requested = Signal()
    strike_toggled = Signal(bool)
    highlight_toggled = Signal(bool)
    clear_format_requested = Signal()
    theme_changed = Signal(str)
    settings_requested = Signal()
    about_requested = Signal()
    help_requested = Signal()
    quit_requested = Signal()

    _ICON_MAP = {
        "btn_sidebar": "panel-left",
        "btn_notes":   "notepad-text",
        "btn_save":    "save",
        "btn_open":    "folder-open",
        "btn_print":   "printer",
        "btn_export":  "download",
        "btn_search":  "search",
        "btn_undo":    "undo-2",
        "btn_redo":    "redo-2",
        "btn_menu":    "menu",
        "btn_new_win": "square-plus",
        "btn_b":       "bold",
        "btn_i":       "italic",
        "btn_u":       "underline",
        "btn_s":       "strikethrough",
        "btn_h":       "highlighter",
        "btn_c":       "eraser",
        "btn_color":   "palette",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolbar")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._icon_color = "#1A1A1A"
        self._icon_size = 18

        main = QHBoxLayout(self)
        main.setContentsMargins(16, 12, 16, 12)
        main.setSpacing(0)
        main.setDirection(QBoxLayout.Direction.RightToLeft)

        main.addWidget(self._build_elements_section())
        main.addWidget(self._sep())
        main.addWidget(self._build_text_section())
        main.addWidget(self._sep())
        main.addWidget(self._build_tools_section())

        self._apply_icons()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 55))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    # ═══════════════════════════════════════════════
    def _apply_icons(self):
        for attr, icon_name in self._ICON_MAP.items():
            btn = getattr(self, attr, None)
            if btn is None:
                continue
            icon = get_icon(icon_name, self._icon_color, self._icon_size)
            btn.setIcon(icon)
            actual = _SIZE_OVERRIDE.get(icon_name, self._icon_size)
            btn.setIconSize(QSize(actual, actual))
            btn.setText("")

    def set_icon_color(self, color: str):
        if color == self._icon_color:
            return
        self._icon_color = color
        self._apply_icons()
        self.size_stepper.set_icon_color(color)

    # ═══════════════════════════════════════════════
    #  بخش ۱: المان‌ها + سایدبار + نوت
    # ═══════════════════════════════════════════════
    def _build_elements_section(self) -> QWidget:
        section = QWidget()

        h = QHBoxLayout(section)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(14)
        h.setDirection(QBoxLayout.Direction.LeftToRight)

        grid = QWidget()
        grid.setLayoutDirection(Qt.RightToLeft)
        v = QVBoxLayout(grid)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(ROW_GAP)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}

        row1 = QHBoxLayout()
        row1.setDirection(QBoxLayout.Direction.RightToLeft)
        row1.setSpacing(6)
        row2 = QHBoxLayout()
        row2.setDirection(QBoxLayout.Direction.RightToLeft)
        row2.setSpacing(6)

        for elem_id in ELEM_ROW1:
            btn = self._make_elem_btn(elem_id)
            self._buttons[elem_id] = btn
            row1.addWidget(btn)
        for elem_id in ELEM_ROW2:
            btn = self._make_elem_btn(elem_id)
            self._buttons[elem_id] = btn
            row2.addWidget(btn)

        v.addLayout(row1)
        v.addLayout(row2)
        h.addWidget(grid)

        side_col = QVBoxLayout()
        side_col.setContentsMargins(0, 0, 0, 0)
        side_col.setSpacing(TOOL_GAP)

        self.btn_sidebar = self._tool_btn("پنل المان‌ها (به‌زودی)")
        self.btn_sidebar.setCheckable(True)
        self.btn_sidebar.setEnabled(False)
        self.btn_sidebar.toggled.connect(self.sidebar_toggled.emit)
        side_col.addWidget(self.btn_sidebar)

        self.btn_notes = self._tool_btn("یادداشت‌ها (به‌زودی)")
        self.btn_notes.setCheckable(True)
        self.btn_notes.setEnabled(False)
        self.btn_notes.toggled.connect(self.notes_toggled.emit)
        side_col.addWidget(self.btn_notes)

        h.addLayout(side_col)
        return section

    # ═══════════════════════════════════════════════
    #  بخش ۲: ابزار متن
    # ═══════════════════════════════════════════════
    def _build_text_section(self) -> QWidget:
        section = QWidget()
        section.setLayoutDirection(Qt.RightToLeft)
        section.setFixedWidth(TEXT_SECTION_W)

        v = QVBoxLayout(section)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(ROW_GAP)

        # ── ردیف ۱: فونت + سایز ──
        row1 = QHBoxLayout()
        row1.setDirection(QBoxLayout.Direction.RightToLeft)
        row1.setSpacing(10)

        self.font_combo = QComboBox()
        self.font_combo.setObjectName("fontCombo")
        self.font_combo.setLayoutDirection(Qt.LeftToRight)
        self.font_combo.setCursor(Qt.PointingHandCursor)
        self.font_combo.setToolTip("فونت متن")
        self.font_combo.setFixedWidth(FONT_COMBO_W)
        self.font_combo.setFixedHeight(ROW_H)
        families = sorted(QFontDatabase.families())
        self.font_combo.addItems(families)
        self.font_combo.setEditable(True)
        le = self.font_combo.lineEdit()
        le.setReadOnly(True)
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        le.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        le.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.font_combo.currentTextChanged.connect(self.font_family_changed.emit)
        row1.addWidget(self.font_combo)

        # ★ استپر سایز فونت — قابل ویرایش (کلیک روی عدد → ویرایش)
        self.size_stepper = Stepper(
            min_val=8, max_val=72, step=1, value=14,
            icon_minus="minus", icon_plus="plus",
            icon_color=self._icon_color,
            spin_width=54, icon_size=16, btn_size=26, spin_height=28,
            click_resets_to=None,
        )
        self.size_stepper.setToolTip("اندازه‌ی فونت")
        self.size_stepper.setFixedWidth(STEPPER_W)
        self.size_stepper.setFixedHeight(ROW_H)
        self.size_stepper.value_changed.connect(self.font_size_changed.emit)
        row1.addWidget(self.size_stepper)

        v.addLayout(row1)

        # ── ردیف ۲: ۷ دکمه‌ی فرمت ──
        row2 = QHBoxLayout()
        row2.setDirection(QBoxLayout.Direction.RightToLeft)
        row2.setSpacing(FORMAT_BTN_GAP)

        self.btn_b = self._format_btn("بولد (Ctrl+B)")
        self.btn_b.toggled.connect(self.bold_toggled.emit)
        row2.addWidget(self.btn_b)

        self.btn_i = self._format_btn("ایتالیک (Ctrl+I)")
        self.btn_i.toggled.connect(self.italic_toggled.emit)
        row2.addWidget(self.btn_i)

        self.btn_u = self._format_btn("زیرخط (Ctrl+U)")
        self.btn_u.toggled.connect(self.underline_toggled.emit)
        row2.addWidget(self.btn_u)

        self.btn_color = self._format_btn("رنگ متن")
        self.btn_color.clicked.connect(self.color_requested.emit)
        row2.addWidget(self.btn_color)

        self.btn_s = self._format_btn("خط‌خورده")
        self.btn_s.toggled.connect(self.strike_toggled.emit)
        row2.addWidget(self.btn_s)

        self.btn_h = self._format_btn("هایلایت")
        self.btn_h.toggled.connect(self.highlight_toggled.emit)
        row2.addWidget(self.btn_h)

        self.btn_c = self._format_btn("پاک کردن فرمت‌ها")
        self.btn_c.clicked.connect(self.clear_format_requested.emit)
        row2.addWidget(self.btn_c)

        v.addLayout(row2)
        return section

    # ═══════════════════════════════════════════════
    #  بخش ۳: ابزارها
    # ═══════════════════════════════════════════════
    def _build_tools_section(self) -> QWidget:
        section = QWidget()
        h = QHBoxLayout(section)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(TOOL_GAP)
        h.setDirection(QBoxLayout.Direction.LeftToRight)

        # ── Col 1 (چپ‌ترین): منو / جستجو ──
        col1 = QVBoxLayout()
        col1.setContentsMargins(0, 0, 0, 0)
        col1.setSpacing(TOOL_GAP)

        self.btn_menu = self._menu_icon_btn("منوی اصلی")
        self.btn_menu.setMenu(self._build_menu())
        col1.addWidget(self.btn_menu)

        self.btn_search = self._tool_btn("جستجو (به‌زودی)")
        self.btn_search.setEnabled(False)
        self.btn_search.clicked.connect(self.search_requested.emit)
        col1.addWidget(self.btn_search)
        h.addLayout(col1)

        # ── Col 2: خروجی / چاپ ──
        col2 = QVBoxLayout()
        col2.setContentsMargins(0, 0, 0, 0)
        col2.setSpacing(TOOL_GAP)

        self.btn_export = self._tool_btn("خروجی (به‌زودی)")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_requested.emit)
        col2.addWidget(self.btn_export)

        self.btn_print = self._tool_btn("چاپ (به‌زودی)")
        self.btn_print.setEnabled(False)
        self.btn_print.clicked.connect(self.print_requested.emit)
        col2.addWidget(self.btn_print)
        h.addLayout(col2)

        # ── Col 3+4: پنل راست ──
        #   ردیف ۱: پنجره‌ی جدید + باز کردن (عرض ۸۲)
        #   ردیف ۲: کپسول Undo/Redo (عرض ۸۲)
        #   → هم‌عرض برای هم‌ترازی
        right_col = QVBoxLayout()
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(TOOL_GAP)

        # ★ ظرف ثابت با عرض CAPSULE_W
        top_row_wrapper = QWidget()
        top_row_wrapper.setFixedSize(CAPSULE_W, TOOL_BTN)

        top_row = QHBoxLayout(top_row_wrapper)
        top_row.setContentsMargins(TOP_ROW_PAD, 0, TOP_ROW_PAD, 0)
        top_row.setSpacing(TOOL_GAP)
        top_row.setDirection(QBoxLayout.Direction.RightToLeft)

        # ★ دکمه‌های ردیف بالا: پهن‌تر (36×34) نسبت به بقیه
        self.btn_new_win = self._top_row_btn("پنجره‌ی جدید")
        self.btn_new_win.clicked.connect(self.new_window_requested.emit)
        top_row.addWidget(self.btn_new_win)

        self.btn_open = self._top_row_btn("باز کردن (Ctrl+O)")
        self.btn_open.clicked.connect(self.open_requested.emit)
        top_row.addWidget(self.btn_open)

        right_col.addWidget(top_row_wrapper)
        right_col.addWidget(self._make_undo_redo_capsule())

        h.addLayout(right_col)
        return section

    def _make_undo_redo_capsule(self) -> QWidget:
        """کپسول افقی که Undo و Redo را کنار هم نگه می‌دارد."""
        capsule = QWidget()
        capsule.setObjectName("undoRedoCapsule")
        capsule.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        capsule.setFixedSize(CAPSULE_W, TOOL_BTN)

        lay = QHBoxLayout(capsule)
        lay.setContentsMargins(CAPSULE_PAD, 0, CAPSULE_PAD, 0)
        lay.setSpacing(TOOL_GAP)
        lay.setDirection(QBoxLayout.Direction.RightToLeft)

        self.btn_undo = self._tool_btn_inner("بازگرداندن (Ctrl+Z)")
        self.btn_undo.clicked.connect(self.undo_requested.emit)
        lay.addWidget(self.btn_undo)

        self.btn_redo = self._tool_btn_inner("ازنو (Ctrl+Shift+Z)")
        self.btn_redo.clicked.connect(self.redo_requested.emit)
        lay.addWidget(self.btn_redo)

        return capsule

    # ═══════════════════════════════════════════════
    #  سازنده‌های دکمه
    # ═══════════════════════════════════════════════
    def _make_elem_btn(self, elem_id: str) -> QPushButton:
        label = ELEMENTS[elem_id]["label_fa"]
        btn = QPushButton(label)
        btn.setObjectName("elemBtn")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(BTN_W, ROW_H)
        btn.clicked.connect(
            lambda checked=False, eid=elem_id: self.element_selected.emit(eid)
        )
        self._group.addButton(btn)
        return btn

    def _format_btn(self, tooltip: str) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("formatBtn")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setFixedSize(FORMAT_BTN_W, ROW_H)
        return btn

    def _tool_btn(self, tooltip: str) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("toolBtn")
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(TOOL_BTN, TOOL_BTN)
        return btn

    def _top_row_btn(self, tooltip: str) -> QPushButton:
        """دکمه‌ی پهن‌تر برای ردیف بالای پنل راست (۳۶px عرض)."""
        btn = QPushButton()
        btn.setObjectName("toolBtn")
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(TOP_BTN_W, TOOL_BTN)
        return btn

    def _tool_btn_inner(self, tooltip: str) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("toolBtnInner")
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(TOOL_BTN, TOOL_BTN)
        return btn

    def _menu_icon_btn(self, tooltip: str) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("menuIconBtn")
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(TOOL_BTN, TOOL_BTN)
        return btn

    def _sep(self) -> QWidget:
        wrapper = QWidget()
        wrapper.setFixedWidth(SEP_W)
        wrapper.setLayoutDirection(Qt.LeftToRight)

        w_layout = QHBoxLayout(wrapper)
        w_layout.setContentsMargins(0, 0, 0, 0)
        w_layout.setSpacing(0)

        line = QFrame()
        line.setObjectName("toolbarSep")
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setFixedWidth(1)
        line.setFixedHeight(SEP_H)

        w_layout.addWidget(line, alignment=Qt.AlignVCenter)
        return wrapper

    # ═══════════════════════════════════════════════
    def _build_menu(self) -> QMenu:
        menu = QMenu(self)
        menu.setLayoutDirection(Qt.RightToLeft)

        try:
            shadow = QGraphicsDropShadowEffect(menu)
            shadow.setBlurRadius(28)
            shadow.setColor(QColor(0, 0, 0, 100))
            shadow.setOffset(0, 6)
            menu.setGraphicsEffect(shadow)
        except Exception:
            pass

        a_new_win = menu.addAction("پنجره‌ی جدید")
        a_new_win.triggered.connect(self.new_window_requested.emit)

        a_open = menu.addAction("باز کردن…")
        a_open.triggered.connect(self.open_requested.emit)

        a_save_as = menu.addAction("ذخیره به‌عنوان…")
        a_save_as.triggered.connect(self.save_as_requested.emit)

        recent_sub = menu.addMenu("فایل‌های اخیر")
        recent_sub.setLayoutDirection(Qt.RightToLeft)
        recent_sub.addAction("(خالی)").setEnabled(False)

        menu.addSeparator()

        a_settings = menu.addAction("تنظیمات…")
        a_settings.triggered.connect(self.settings_requested.emit)

        theme_sub = menu.addMenu("ظاهر")
        theme_sub.setLayoutDirection(Qt.RightToLeft)
        a_light = theme_sub.addAction("روشن")
        a_light.triggered.connect(lambda: self.theme_changed.emit("light"))
        a_dark = theme_sub.addAction("تاریک")
        a_dark.triggered.connect(lambda: self.theme_changed.emit("dark"))
        a_auto = theme_sub.addAction("بر اساس سیستم")
        a_auto.triggered.connect(lambda: self.theme_changed.emit("default"))

        menu.addSeparator()

        a_help = menu.addAction("راهنما")
        a_help.triggered.connect(self.help_requested.emit)

        a_about = menu.addAction("درباره‌ی فیلم‌نویس")
        a_about.triggered.connect(self.about_requested.emit)

        menu.addSeparator()

        a_quit = menu.addAction("خروج")
        a_quit.triggered.connect(self.quit_requested.emit)

        return menu

    # ═══════════════════════════════════════════════
    def set_active_element(self, elem_id: str):
        btn = self._buttons.get(elem_id)
        if btn and not btn.isChecked():
            btn.setChecked(True)

    def set_font_family(self, family: str):
        self.font_combo.blockSignals(True)
        idx = self.font_combo.findText(family)
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        self.font_combo.blockSignals(False)

    def set_font_size(self, size: int):
        self.size_stepper.set_value(size)
