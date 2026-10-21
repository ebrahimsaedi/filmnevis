"""بارگذاری فونت‌های برنامه و سیستم."""

from pathlib import Path

from PySide6.QtGui import QFontDatabase


_LOADED: list[str] = []


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_project_fonts() -> list[str]:
    """فونت‌های داخل پوشه‌ی data/fonts را بارگذاری می‌کند."""
    fonts_dir = _project_root() / "data" / "fonts"
    loaded: list[str] = []
    if not fonts_dir.is_dir():
        return loaded

    for font_file in sorted(fonts_dir.glob("*.ttf")):
        fid = QFontDatabase.addApplicationFont(str(font_file))
        if fid >= 0:
            families = QFontDatabase.applicationFontFamilies(fid)
            loaded.extend(families)
    _LOADED.extend(loaded)
    return loaded


def available_families() -> list[str]:
    """همه‌ی خانواده‌های فونت موجود (سیستم + برنامه)."""
    return sorted(QFontDatabase.families())


def has_family(name: str) -> bool:
    """آیا فونتی با این نام موجود است؟"""
    return name in QFontDatabase.families()
