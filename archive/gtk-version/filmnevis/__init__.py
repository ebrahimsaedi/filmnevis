"""فیلمنویس — ویرایشگر فیلمنامه‌ی فارسی."""

__version__ = "0.1.0"
__app_id__ = "com.ebrahimsaedi.Filmnevis"
__app_name__ = "فیلمنویس"


import os
import tempfile
from pathlib import Path


def _setup_fonts() -> None:
    """فونت‌های پروژه را پیش از راه‌اندازی GTK به fontconfig معرفی می‌کند.

    با این کار، فونت B Nazanin که داخل پوشه‌ی پروژه است، بدون نصب
    روی سیستم در دسترس Pango قرار می‌گیرد. سیستم کاربر دست‌نخورده
    می‌ماند و نیازی به کپی دستی در ~/.local/share/fonts نیست.
    """
    project_root = Path(__file__).resolve().parent.parent
    fonts_dir = project_root / "data" / "fonts"

    if not fonts_dir.is_dir():
        return

    cache_dir = Path(tempfile.gettempdir()) / "filmnevis-fontconfig"
    (cache_dir / "cache").mkdir(parents=True, exist_ok=True)

    conf_path = cache_dir / "fonts.conf"
    conf_path.write_text(
        "<?xml version=\"1.0\"?>\n"
        "<!DOCTYPE fontconfig SYSTEM \"fonts.dtd\">\n"
        "<fontconfig>\n"
        "  <include ignore_missing=\"yes\">/etc/fonts/fonts.conf</include>\n"
        f"  <dir>{fonts_dir}</dir>\n"
        f"  <cachedir>{cache_dir / 'cache'}</cachedir>\n"
        "</fontconfig>\n",
        encoding="utf-8",
    )

    os.environ["FONTCONFIG_FILE"] = str(conf_path)


_setup_fonts()
