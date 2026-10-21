"""تم‌های روشن و تاریک — هویت «شب» برای فیلم‌نویس.

فلسفه:
    UI میاد عقب، نوشتن میاد جلو.
    کاغذ، تنها چیز روشن صحنه است.
    رنگ تأکیدی وجود ندارد — فقط سیاه و سفید.

سلامت چشم:
    همه‌ی کنتراست‌ها توی باند ۷-۱۲:۱ (طلایی برای خواندن طولانی).
    هیچ سفید/مشکی مطلق نیست.
    همه‌ی رنگ‌ها ته‌رنگ گرم دارن (کاهش نور آبی).
    کاغذ و متن، هم‌خانواده‌ی رنگی هستن.
"""

# ═══════════════════════════════════════════════
#  حالت روشن — «کاغذ کتاب»
# ═══════════════════════════════════════════════
LIGHT = {
    "bg":            "#E5DECE",
    "bg_alt":        "#DAD3C0",
    "toolbar_bg":    "#E5DECE",
    "toolbar_border": "#D0C8B3",
    "panel":         "#FAF6EB",
    "panel_alt":     "#F0EAD9",
    "paper":         "#FAF6EB",
    "text":          "#3A3428",
    "text_dim":      "#4A4238",
    "text_muted":    "#A89E8A",
    "border":        "#D0C8B3",
    "border_strong": "#B8AF98",
    "accent":        "#3A3428",
    "accent_fg":     "#FAF6EB",
    "paper_mark":    "#B8935A",
    "text_on_paper": "#2A2520",
    "selection_bg":  "#E8D9B0",
    "selection_fg":  "#2A2520",
    "tooltip_bg":    "#3A3428",
    "tooltip_fg":    "#FAF6EB",
    "shadow_color_tuple": (0, 0, 0),
    "shadow_alpha":       100,
    "shadow_offset_y":    2,
}

# ═══════════════════════════════════════════════
#  حالت تاریک — «شب مطالعه»
# ═══════════════════════════════════════════════
DARK = {
    "bg":            "#1A1613",
    "bg_alt":        "#25201C",
    "toolbar_bg":    "#1A1613",
    "toolbar_border": "#2E2824",
    "panel":         "#221D19",
    "panel_alt":     "#2A2520",
    "paper":         "#DED6C0",
    "text":          "#D8D0BC",
    "text_dim":      "#A89E8A",
    "text_muted":    "#5A5248",
    "border":        "#2E2824",
    "border_strong": "#423C35",
    "accent":        "#D8D0BC",
    "accent_fg":     "#1A1613",
    "paper_mark":    "#B8935A",
    "text_on_paper": "#2A2520",
    "selection_bg":  "#4A3E2A",
    "selection_fg":  "#F0E8D8",
    "tooltip_bg":    "#F0E8D8",
    "tooltip_fg":    "#1A1613",
    "shadow_color_tuple": (255, 255, 255),
    "shadow_alpha":       28,
    "shadow_offset_y":    0,
}


def get_colors(scheme: str) -> dict:
    if scheme == "dark":
        return DARK
    return LIGHT


def get_qss(scheme: str) -> str:
    c = get_colors(scheme)
    return f"""
/* ═══ پنجره و زمینه ═══ */
QMainWindow {{ background-color: {c['bg']}; }}

QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: {c['bg']};
    border: none;
}}

QWidget#pageContainer {{ background-color: {c['bg']}; }}

/* ═══ نوارهای شناور ═══ */
QWidget#toolbar {{
    background-color: {c['toolbar_bg']};
    border: 1px solid {c['toolbar_border']};
    border-radius: 16px;
}}

QWidget#statusbar {{
    background-color: {c['toolbar_bg']};
    border: 1px solid {c['toolbar_border']};
    border-radius: 16px;
}}

QFrame#toolbarSep {{
    background-color: {c['border']};
    border: none;
}}

QLabel#statusLabel {{
    color: {c['text_dim']};
    font-family: "Sahel";
    font-size: 11pt;
}}

/* ═══ دکمه‌های المان ═══ */
QPushButton#elemBtn {{
    background-color: transparent;
    color: {c['text']};
    border: 1px solid {c['border_strong']};
    border-radius: 10px;
    padding: 0;
    font-family: "Sahel";
    font-size: 11pt;
}}

QPushButton#elemBtn:hover {{
    background-color: {c['bg_alt']};
}}

QPushButton#elemBtn:pressed {{
    background-color: {c['border']};
}}

QPushButton#elemBtn:checked {{
    background-color: {c['accent']};
    color: {c['accent_fg']};
    border: 1px solid {c['accent']};
}}

/* ═══ دکمه‌های فرمت ═══ */
QPushButton#formatBtn {{
    background-color: transparent;
    color: {c['text']};
    border: 1px solid {c['border_strong']};
    border-radius: 10px;
    padding: 0;
    font-family: "Sahel";
    font-size: 13pt;
    font-weight: bold;
}}

QPushButton#formatBtn:hover {{
    background-color: {c['bg_alt']};
}}

QPushButton#formatBtn:checked {{
    background-color: {c['accent']};
    color: {c['accent_fg']};
    border: 1px solid {c['accent']};
}}

/* ═══ دکمه‌های ابزار (با کپسول) ═══ */
QPushButton#toolBtn {{
    background-color: transparent;
    color: {c['text']};
    border: 1px solid {c['border_strong']};
    border-radius: 10px;
    padding: 0;
    font-size: 13pt;
    font-weight: 500;
}}

QPushButton#toolBtn:hover {{
    background-color: {c['bg_alt']};
}}

QPushButton#toolBtn:pressed {{
    background-color: {c['border']};
}}

QPushButton#toolBtn:disabled {{
    color: {c['text_muted']};
}}

QPushButton#toolBtn::menu-indicator {{
    image: none;
    width: 0px;
    height: 0px;
}}

/* ═══ Undo+Redo در یک کپسول ═══ */
QWidget#undoRedoCapsule {{
    background-color: transparent;
    border: 1px solid {c['border_strong']};
    border-radius: 10px;
}}

QPushButton#toolBtnInner {{
    background-color: transparent;
    color: {c['text']};
    border: none;
    border-radius: 8px;
    padding: 0;
    font-size: 13pt;
    font-weight: 500;
}}

QPushButton#toolBtnInner:hover {{
    background-color: {c['bg_alt']};
}}

QPushButton#toolBtnInner:pressed {{
    background-color: {c['border']};
}}

QPushButton#toolBtnInner:disabled {{
    color: {c['text_muted']};
}}

/* ═══ دکمه‌ی منو (بدون کپسول) ═══ */
QPushButton#menuIconBtn {{
    background-color: transparent;
    color: {c['text']};
    border: none;
    border-radius: 10px;
    padding: 0;
    font-size: 13pt;
    font-weight: 500;
}}

QPushButton#menuIconBtn:hover {{
    background-color: {c['bg_alt']};
}}

QPushButton#menuIconBtn:pressed {{
    background-color: {c['border']};
}}

QPushButton#menuIconBtn::menu-indicator {{
    image: none;
    width: 0px;
    height: 0px;
}}

/* ═══ کمبوباکس فونت ═══ */
QComboBox#fontCombo {{
    background-color: transparent;
    color: {c['text']};
    border: 1px solid {c['border_strong']};
    border-radius: 10px;
    padding: 0 12px;
    font-family: "Sahel";
    font-size: 11pt;
}}

QComboBox#fontCombo:hover {{
    background-color: {c['bg_alt']};
}}

QComboBox#fontCombo::drop-down {{
    border: none;
    width: 18px;
    subcontrol-origin: padding;
    subcontrol-position: center left;
}}

QComboBox#fontCombo QLineEdit {{
    background: transparent;
    border: none;
    color: {c['text']};
    padding: 0;
    margin: 0;
}}

QComboBox#fontCombo QAbstractItemView {{
    background-color: {c['panel']};
    color: {c['text']};
    border: 1px solid {c['border_strong']};
    border-radius: 10px;
    padding: 4px;
    outline: none;
    selection-background-color: {c['selection_bg']};
    selection-color: {c['selection_fg']};
    font-family: "Sahel";
    font-size: 11pt;
}}

/* ═══ Stepper — بدون کادر بیرونی، عدد در کپسول ═══ */
QWidget#stepper {{
    background-color: transparent;
    border: none;
}}

QPushButton#stepperIconBtn {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 0;
}}

QPushButton#stepperIconBtn:hover {{
    background-color: {c['bg_alt']};
}}

QPushButton#stepperIconBtn:pressed {{
    background-color: {c['border']};
}}

QSpinBox#stepperSpin {{
    background-color: transparent;
    color: {c['text']};
    border: 1px solid {c['border_strong']};
    border-radius: 14px;
    font-family: "Sahel";
    font-size: 11pt;
    padding: 0 6px;
}}

QSpinBox#stepperSpin:focus {{
    background-color: {c['bg_alt']};
    border: 1px solid {c['text_dim']};
}}

/* ═══ ویرایشگر ═══ */
QTextEdit#screenplayEditor {{
    background-color: transparent;
    color: {c['text_on_paper']};
    border: none;
    padding: 0;
    selection-background-color: {c['selection_bg']};
    selection-color: {c['selection_fg']};
}}

/* ═══ منو ═══ */
QMenu {{
    background-color: {c['panel']};
    border: 1px solid {c['border_strong']};
    border-radius: 14px;
    padding: 8px;
    font-family: "Sahel";
    font-size: 11pt;
    color: {c['text']};
}}

QMenu::item {{
    padding: 8px 24px 8px 32px;
    border-radius: 8px;
    color: {c['text']};
}}

QMenu::item:selected {{
    background-color: {c['bg_alt']};
    color: {c['text']};
}}

QMenu::item:disabled {{
    color: {c['text_dim']};
}}

QMenu::separator {{
    height: 1px;
    background-color: {c['border']};
    margin: 6px 12px;
}}

QMenu::right-arrow {{
    width: 10px;
    height: 10px;
    margin-right: 8px;
}}

/* ═══ Tooltip ═══ */
QToolTip {{
    background-color: {c['tooltip_bg']};
    color: {c['tooltip_fg']};
    border: none;
    border-radius: 8px;
    padding: 6px 12px;
    font-family: "Sahel";
    font-size: 10pt;
}}

/* ═══ اسکرول‌بار ═══ */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 0;
    border: none;
}}

QScrollBar::handle:vertical {{
    background-color: {c['border_strong']};
    min-height: 30px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c['text_dim']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0; border: none; background: none;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 0;
    border: none;
}}

QScrollBar::handle:horizontal {{
    background-color: {c['border_strong']};
    min-width: 30px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {c['text_dim']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0; border: none; background: none;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

QScrollBar::corner {{
    background: transparent;
    border: none;
}}

/* ═══ فوکوس روی دکمه‌ها ═══ */
QPushButton:focus {{
    outline: none;
    border: 1px solid {c['text_dim']};
}}

/* ═══ دیالوگ‌ها ═══ */
QDialog {{
    background-color: {c['panel']};
    color: {c['text']};
}}

QLabel {{
    color: {c['text']};
    font-family: "Sahel";
}}

QLineEdit, QListWidget, QSpinBox {{
    background-color: {c['bg']};
    color: {c['text']};
    border: 1px solid {c['border_strong']};
    border-radius: 10px;
    padding: 6px 12px;
    font-family: "Sahel";
    font-size: 11pt;
    selection-background-color: {c['selection_bg']};
    selection-color: {c['selection_fg']};
}}

QLineEdit:focus, QListWidget:focus {{
    border: 1px solid {c['text_dim']};
}}

QListWidget::item {{
    padding: 6px 10px;
    border-radius: 6px;
    color: {c['text']};
}}

QListWidget::item:selected {{
    background-color: {c['selection_bg']};
    color: {c['selection_fg']};
}}

QListWidget::item:hover {{
    background-color: {c['bg_alt']};
}}

QMessageBox {{
    background-color: {c['panel']};
    color: {c['text']};
}}

QMessageBox QLabel {{
    color: {c['text']};
}}

QMessageBox QPushButton {{
    min-width: 90px;
    padding: 6px 20px;
}}

QMessageBox QPushButton:default {{
    background-color: {c['accent']};
    color: {c['accent_fg']};
    border: 1px solid {c['accent']};
}}
"""
