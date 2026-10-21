"""راه‌اندازی QApplication."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from filmnevis import __app_name__
from filmnevis.fonts import load_project_fonts
from filmnevis.settings import load_settings, save_settings
from filmnevis.theme import get_colors, get_qss
from filmnevis.window import FilmnevisWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setLayoutDirection(Qt.RightToLeft)

    load_project_fonts()
    settings = load_settings()

    win = FilmnevisWindow()

    def apply_theme(scheme: str):
        app.setStyleSheet(get_qss(scheme))
        colors = get_colors(scheme)
        win.toolbar.set_icon_color(colors["text"])
        win.apply_theme_visuals(scheme)

    apply_theme(settings.get("color_scheme", "light"))

    def on_theme_change(scheme: str):
        settings["color_scheme"] = scheme
        save_settings(settings)
        apply_theme(scheme)

    win.toolbar.theme_changed.connect(on_theme_change)

    def on_about():
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            win, "درباره‌ی فیلم‌نویس",
            "فیلم‌نویس — ویرایشگر فیلم‌نامه‌ی فارسی\n"
            "نسخه: 0.2.0\n"
            "ساخته‌ی ابراهیم ساعدی",
        )

    win.toolbar.about_requested.connect(on_about)
    win.toolbar.quit_requested.connect(win.close)

    win.show()
    return app.exec()
