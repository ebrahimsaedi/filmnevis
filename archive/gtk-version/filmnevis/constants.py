"""مشخصات فنی قالب فیلمنامه — آینه‌ی استاندارد انگلیسی برای فارسی."""

# --- ابعاد صفحه (میلی‌متر) ---
PAGE_WIDTH_MM = 210.0
PAGE_HEIGHT_MM = 297.0

# --- حاشیه‌ها (میلی‌متر) ---
# استاندارد فیلمنامه‌ی انگلیسی:
#   حاشیه‌ی چپ: ۱.۵ اینچ (۳۸.۱ mm) — شروع متن
#   حاشیه‌ی راست: ۱ اینچ (۲۵.۴ mm) — پایان متن
#
# آینه‌شده برای فارسی (راست‌چین):
#   حاشیه‌ی راست کاغذ: ۳۸.۱ mm — شروع متن فارسی
#   حاشیه‌ی چپ کاغذ: ۲۵.۴ mm — پایان متن فارسی
MARGIN_TOP_MM = 25.4
MARGIN_BOTTOM_MM = 25.4
MARGIN_RIGHT_MM = 38.1   # فاصله از لبه‌ی راست کاغذ
MARGIN_LEFT_MM = 25.4    # فاصله از لبه‌ی چپ کاغذ

# --- ناحیه‌ی متن ---
TEXT_WIDTH_MM = PAGE_WIDTH_MM - MARGIN_RIGHT_MM - MARGIN_LEFT_MM
TEXT_HEIGHT_MM = PAGE_HEIGHT_MM - MARGIN_TOP_MM - MARGIN_BOTTOM_MM

# --- فونت ---
FONT_FAMILY = "B Nazanin"
FONT_SIZE_PT = 14

# --- فاصله‌ی بین پاراگراف‌ها ---
BLANK_LINE_PX = 20

# --- فاصله‌ی بین خطوط ---
LINE_SPACING_BELOW_PX = 4

# --- تبدیل واحد ---
PX_PER_MM = 96.0 / 25.4


def mm_to_px(mm: float) -> int:
    return int(round(mm * PX_PER_MM))


# --- مشخصات المان‌های فیلمنامه ---
ELEMENTS = {
    "scene": {
        "label_fa": "صحنه",
        "indent_right_mm": 0.0,
        "space_before_px": BLANK_LINE_PX,
        "next": "action",
    },
    "action": {
        "label_fa": "توصیف",
        "indent_right_mm": 0.0,
        "space_before_px": 0,
        "next": "scene",
    },
    "character": {
        "label_fa": "شخصیت",
        "indent_right_mm": 55.9,
        "space_before_px": BLANK_LINE_PX,
        "next": "dialogue",
    },
    "parenthetical": {
        "label_fa": "توضیح",
        "indent_right_mm": 40.6,
        "space_before_px": 0,
        "next": "dialogue",
    },
    "dialogue": {
        "label_fa": "دیالوگ",
        "indent_right_mm": 25.4,
        "space_before_px": 0,
        "next": "character",
    },
    "transition": {
        "label_fa": "گذار",
        "indent_right_mm": 0.0,
        "space_before_px": BLANK_LINE_PX,
        "next": "scene",
        "push_left_mm": 110.0,
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
