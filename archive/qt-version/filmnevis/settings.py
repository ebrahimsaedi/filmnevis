"""ذخیره و بازیابی تنظیمات کاربر در ~/.config/filmnevis/settings.json."""

import json
from pathlib import Path


SETTINGS_DIR = Path.home() / ".config" / "filmnevis"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

_DEFAULTS = {
    "color_scheme": "default",     # default | light | dark
    "font_family_text": None,       # None = استفاده از پیش‌فرض
    "font_size_pt": None,           # None = استفاده از پیش‌فرض
    "zoom_level": 1.0,              # 0.25 تا 3.0
}


def load_settings() -> dict:
    """تنظیمات را می‌خواند. اگر فایل نبود، مقادیر پیش‌فرض را برمی‌گرداند."""
    data = dict(_DEFAULTS)
    if SETTINGS_FILE.is_file():
        try:
            loaded = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data.update(loaded)
        except Exception:
            pass
    return data


def save_settings(data: dict) -> None:
    """تنظیمات را ذخیره می‌کند."""
    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass
