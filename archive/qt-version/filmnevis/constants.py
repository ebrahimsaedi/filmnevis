"""مشخصات فنی قالب فیلمنامه و برنامه."""

PAGE_WIDTH_MM = 210.0
PAGE_HEIGHT_MM = 297.0

MARGIN_TOP_MM = 25.4
MARGIN_BOTTOM_MM = 25.4
MARGIN_RIGHT_MM = 38.1
MARGIN_LEFT_MM = 25.4

FONT_FAMILY_UI = "Sahel"
FONT_FAMILY_TEXT = "Sahel"
FONT_FAMILY_FALLBACK = "B Nazanin"

FONT_SIZE_PT = 14

BLANK_LINE_PX = 14

ELEMENTS = {
    "scene": {
        "label_fa": "صحنه",
        "indent_right_mm": 0.0,
        "space_before_px": BLANK_LINE_PX,
        "bold": False,
        "align": "right",
        "next": "action",
    },
    "action": {
        "label_fa": "توصیف",
        "indent_right_mm": 0.0,
        "space_before_px": BLANK_LINE_PX,   # ← از 0 به BLANK_LINE_PX
        "bold": False,
        "align": "right",
        "next": "scene",
    },
    "character": {
        "label_fa": "شخصیت",
        "indent_right_mm": 55.9,
        "space_before_px": BLANK_LINE_PX,
        "bold": False,
        "align": "right",
        "next": "dialogue",
    },
    "parenthetical": {
        "label_fa": "توضیح",
        "indent_right_mm": 40.6,
        "space_before_px": 0,
        "bold": False,
        "align": "right",
        "next": "dialogue",
    },
    "dialogue": {
        "label_fa": "دیالوگ",
        "indent_right_mm": 25.4,
        "space_before_px": 0,
        "bold": False,
        "align": "right",
        "next": "character",
    },
    "transition": {
        "label_fa": "گذار",
        "indent_right_mm": 0.0,
        "space_before_px": BLANK_LINE_PX,
        "bold": False,
        "align": "left",
        "next": "scene",
        "push_left_mm": 100.0,
    },
}

ELEMENT_ORDER = [
    "scene", "action", "character",
    "parenthetical", "dialogue", "transition",
]

DOCUMENT_TYPES = {
    "screenplay": "فیلمنامه",
    "prose":      "متن معمولی",
}

PX_PER_MM = 96.0 / 25.4


def mm_to_px(mm: float) -> float:
    return mm * PX_PER_MM


ZWNJ = "\u200c"
INVISIBLE_CHARS = "\u200b\u200c\u200d\u200e\u200f\ufeff"


def strip_invisible(text: str) -> str:
    return "".join(c for c in text if c not in INVISIBLE_CHARS)
