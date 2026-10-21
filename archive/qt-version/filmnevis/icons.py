"""بارگذاری و رندر آیکون‌های SVG با رنگ پویا."""

from pathlib import Path

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


_ICONS_DIR = Path(__file__).resolve().parent.parent / "data" / "icons"
_cache: dict = {}

# تنظیم اندازه‌ی اختصاصی — بعضی آیکون‌ها به‌خاطر padding ذاتی SVG
# کوچیک‌تر دیده می‌شن، اینا رو بزرگ‌تر می‌کنیم.
_SIZE_OVERRIDE = {
    "menu":         22,
    "save":         20,
    "folder-open":  20,
    "printer":      20,
    "search":       20,
    "square-plus":  19,
    "panel-left":   19,
    "notepad-text": 19,
}


def _svg_content(name: str) -> str:
    path = _ICONS_DIR / f"{name}.svg"
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def get_icon(name: str, color: str, size: int = 18) -> QIcon:
    """آیکون SVG را با رنگ مشخص رندر می‌کند."""
    actual_size = _SIZE_OVERRIDE.get(name, size)

    key = (name, color, actual_size)
    cached = _cache.get(key)
    if cached is not None:
        return cached

    svg = _svg_content(name)
    if not svg:
        return QIcon()

    svg_colored = svg.replace("currentColor", color)

    renderer = QSvgRenderer(QByteArray(svg_colored.encode("utf-8")))
    pixmap = QPixmap(actual_size, actual_size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    try:
        renderer.render(painter)
    finally:
        painter.end()

    icon = QIcon(pixmap)
    _cache[key] = icon
    return icon


def clear_cache():
    _cache.clear()
