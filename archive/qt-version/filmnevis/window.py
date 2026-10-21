"""پنجره‌ی اصلی فیلم‌نویس."""

from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QKeySequence, QPainter, QPen, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from filmnevis import __app_name__
from filmnevis.constants import (
    PAGE_WIDTH_MM, PAGE_HEIGHT_MM,
    MARGIN_TOP_MM, MARGIN_BOTTOM_MM,
    MARGIN_LEFT_MM, MARGIN_RIGHT_MM,
    ELEMENTS, mm_to_px,
)
from filmnevis.document import FILE_EXT, ScreenplayDocument
from filmnevis.editor import FilmnevisEditor
from filmnevis.font_dialog import FontPickerDialog
from filmnevis.settings import load_settings, save_settings
from filmnevis.statusbar import CountersBar, ZoomBar
from filmnevis.theme import get_colors
from filmnevis.toolbar import FilmnevisToolbar
from filmnevis.widgets import ShadowWrapper


FILE_FILTER = f"فیلم‌نویس (*{FILE_EXT});;همه‌ی فایل‌ها (*)"

TOP_ZONE = 130
BOTTOM_ZONE = 100
EDGE_MARGIN = 2
SHADOW_ROOM = 2

CONTENT_WIDTH = 900
PAPER_CORNER_RADIUS = 6


def _shadow_qcolor(colors: dict) -> QColor:
    r, g, b = colors.get("shadow_color_tuple", (0, 0, 0))
    a = colors.get("shadow_alpha", 90)
    return QColor(r, g, b, a)


def _shadow_offset(colors: dict) -> int:
    return colors.get("shadow_offset_y", 2)


class PaperWidget(QWidget):
    """برگه‌ی A4 پیوسته با گوشه‌های گرد و رنگ قابل تنظیم."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scale = 1.0
        self._page_height = int(mm_to_px(PAGE_HEIGHT_MM))
        self._paper_color = QColor(255, 255, 255)
        self._mark_color = QColor(180, 180, 180)

    def set_scale(self, scale: float):
        self._scale = scale
        self._page_height = int(mm_to_px(PAGE_HEIGHT_MM) * scale)
        self.update()

    def set_paper_color(self, color: QColor):
        self._paper_color = QColor(color)
        self.update()

    def set_mark_color(self, color: QColor):
        self._mark_color = QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._paper_color)
        p.drawRoundedRect(self.rect(),
                          PAPER_CORNER_RADIUS, PAPER_CORNER_RADIUS)

        pen = QPen(self._mark_color)
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)

        l = mm_to_px(MARGIN_LEFT_MM) * self._scale
        r = self.width() - mm_to_px(MARGIN_RIGHT_MM) * self._scale
        top = mm_to_px(MARGIN_TOP_MM) * self._scale
        mark = 10

        def corners(t):
            p.drawLine(int(r - mark), int(t), int(r), int(t))
            p.drawLine(int(r), int(t), int(r), int(t + mark))
            p.drawLine(int(l), int(t), int(l + mark), int(t))
            p.drawLine(int(l), int(t), int(l), int(t + mark))

        corners(top)
        y = self._page_height
        while y < self.height():
            corners(y + top)
            y += self._page_height

        p.end()


class OverlayHost(QWidget):
    """ظرف شفاف برای نگه‌داشتن نوارهای شناور."""

    def __init__(self, parent=None, scroll_ref=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self._scroll_ref = scroll_ref

    def wheelEvent(self, event):
        sa = self._scroll_ref
        if sa is not None:
            vbar = sa.verticalScrollBar()
            delta = event.angleDelta().y()
            vbar.setValue(vbar.value() - delta)
            event.accept()
            return
        super().wheelEvent(event)


class FilmnevisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(__app_name__)
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(1280, 900)
        self.setMinimumSize(820, 560)

        self.settings = load_settings()
        self.current_file: Path | None = None
        self._dirty = False
        self._suppress_dirty = False

        central = QWidget()
        self.setCentralWidget(central)

        # ── اسکرول اریا ──
        self.scroll = QScrollArea(central)
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.scroll.setFrameShape(QScrollArea.NoFrame)

        scroll_inner = QWidget()
        scroll_inner.setObjectName("pageContainer")
        scroll_inner_layout = QVBoxLayout(scroll_inner)
        scroll_inner_layout.setContentsMargins(40, TOP_ZONE, 40, BOTTOM_ZONE)
        scroll_inner_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.scroll.setWidget(scroll_inner)

        self._paper = PaperWidget()
        self._paper.setObjectName("pageWidget")
        self._paper.setFixedWidth(int(mm_to_px(PAGE_WIDTH_MM)))
        self._paper.setMinimumHeight(int(mm_to_px(PAGE_HEIGHT_MM)))

        shadow = QGraphicsDropShadowEffect(self._paper)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 65))
        shadow.setOffset(0, 5)
        self._paper.setGraphicsEffect(shadow)

        self._paper_layout = QVBoxLayout(self._paper)
        self._paper_layout.setSpacing(0)
        self._apply_paper_margins(1.0)

        self.editor = FilmnevisEditor()
        self.editor.setObjectName("screenplayEditor")
        self._paper_layout.addWidget(self.editor)

        scroll_inner_layout.addWidget(self._paper, alignment=Qt.AlignHCenter)

        # ═══════════════════════════════════════════
        #  OVERLAY بالا
        # ═══════════════════════════════════════════
        self.top_overlay = OverlayHost(central, scroll_ref=self.scroll)
        top_layout = QHBoxLayout(self.top_overlay)
        top_layout.setContentsMargins(EDGE_MARGIN, SHADOW_ROOM,
                                      EDGE_MARGIN, SHADOW_ROOM)
        top_layout.setSpacing(0)

        top_layout.addStretch(1)

        self.toolbar = FilmnevisToolbar()
        self.toolbar.setFixedWidth(CONTENT_WIDTH)
        self.toolbar.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, False
        )

        self._toolbar_wrap = ShadowWrapper(
            self.toolbar, pad=18, blur=26,
            color=QColor(0, 0, 0, 90), offset_y=2,
        )
        self._toolbar_wrap.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, False
        )
        top_layout.addWidget(self._toolbar_wrap)

        top_layout.addStretch(1)

        # ═══════════════════════════════════════════
        #  OVERLAY پایین
        # ═══════════════════════════════════════════
        self.bottom_overlay = OverlayHost(central, scroll_ref=self.scroll)
        bot_outer = QHBoxLayout(self.bottom_overlay)
        bot_outer.setContentsMargins(EDGE_MARGIN, SHADOW_ROOM,
                                     EDGE_MARGIN, SHADOW_ROOM)
        bot_outer.setSpacing(0)

        bot_outer.addStretch(1)

        bot_inner = QWidget()
        bot_inner.setFixedWidth(CONTENT_WIDTH + 36)
        bot_outer.addWidget(bot_inner)

        bot_outer.addStretch(1)

        bot_layout = QHBoxLayout(bot_inner)
        bot_layout.setContentsMargins(0, 0, 0, 0)
        bot_layout.setSpacing(0)

        self.counters = CountersBar()
        self.zoom_bar = ZoomBar()
        self.counters.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, False
        )
        self.zoom_bar.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, False
        )

        self._counters_wrap = ShadowWrapper(
            self.counters, pad=18, blur=26,
            color=QColor(0, 0, 0, 90), offset_y=2,
        )
        self._counters_wrap.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, False
        )

        self._zoom_wrap = ShadowWrapper(
            self.zoom_bar, pad=18, blur=26,
            color=QColor(0, 0, 0, 90), offset_y=2,
        )
        self._zoom_wrap.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, False
        )

        bot_layout.addWidget(self._counters_wrap)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Preferred)
        bot_layout.addWidget(spacer)

        bot_layout.addWidget(self._zoom_wrap)

        # ═══════════════════════════════════════════
        #  اتصال‌ها
        # ═══════════════════════════════════════════
        self.toolbar.element_selected.connect(self.editor.set_current_element)
        self.editor.element_changed.connect(self._on_element_changed)
        self.editor.zoom_changed.connect(self._on_zoom_changed)
        self.editor.layout_changed.connect(self._on_layout_changed)

        self.toolbar.undo_requested.connect(self.editor.undo)
        self.toolbar.redo_requested.connect(self.editor.redo)

        self.toolbar.open_requested.connect(self._open_document)
        self.toolbar.save_requested.connect(self._save_document)
        self.toolbar.save_as_requested.connect(self._save_document_as)

        self.toolbar.font_family_changed.connect(self._on_font_family_changed)
        self.toolbar.font_size_changed.connect(self._on_font_size_changed)

        self.toolbar.new_window_requested.connect(self._new_window)
        self.toolbar.settings_requested.connect(self._open_settings)
        self.toolbar.help_requested.connect(self._open_help)

        self.zoom_bar.zoom_changed.connect(self._on_zoom_stepper)

        self.editor.document().contentsChanged.connect(self._on_contents_changed)

        QShortcut(QKeySequence("Ctrl+O"), self, self._open_document)
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_document)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self._save_document_as)

        self._apply_saved_font()
        self._update_stats()
        self.zoom_bar.set_zoom(100)
        self.editor.setFocus()

        QTimer.singleShot(100, self._relayout)
        QTimer.singleShot(300, self._mark_initial_clean)

    # ═══════════════════════════════════════════════
    def apply_theme_visuals(self, scheme: str):
        """تمام عناصر بصری را با تم جدید هماهنگ می‌کند."""
        colors = get_colors(scheme)

        shadow_color = _shadow_qcolor(colors)
        offset = _shadow_offset(colors)
        for wrap in (self._toolbar_wrap, self._counters_wrap, self._zoom_wrap):
            wrap.set_shadow_color(shadow_color)
            wrap.set_shadow_offset(offset)

        self._paper.set_paper_color(QColor(colors["paper"]))
        self._paper.set_mark_color(QColor(colors["paper_mark"]))

        # ★ رنگ آیکون‌های استپرها
        self.toolbar.set_icon_color(colors["text"])
        self.zoom_bar.set_icon_color(colors["text"])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._relayout()

    def _relayout(self):
        cw = self.centralWidget()
        if cw is None:
            return
        w = cw.width()
        h = cw.height()

        self.scroll.setGeometry(0, 0, w, h)

        top_h = self.top_overlay.sizeHint().height() or 130
        self.top_overlay.setGeometry(0, 0, w, top_h)
        self.top_overlay.raise_()

        bot_h = self.bottom_overlay.sizeHint().height() or 100
        self.bottom_overlay.setGeometry(0, h - bot_h, w, bot_h)
        self.bottom_overlay.raise_()

    def _mark_initial_clean(self):
        self._dirty = False
        self._update_title()

    # ═══════════════════════════════════════════════
    def _on_font_family_changed(self, family: str):
        if not family:
            return
        self.editor.set_text_font_family(family)
        self.settings["font_family_text"] = family
        save_settings(self.settings)

    def _on_font_size_changed(self, size: int):
        if size <= 0:
            return
        self.editor.set_text_font_size(size)
        self.settings["font_size_pt"] = size
        save_settings(self.settings)

    def _on_zoom_stepper(self, percent: int):
        try:
            self.editor.set_zoom(percent)
            self._on_zoom_changed(percent)
        except AttributeError:
            pass

    def _apply_saved_font(self):
        fam = self.settings.get("font_family_text")
        if fam:
            self.editor.set_text_font_family(fam)
            self.toolbar.set_font_family(fam)
        size = self.settings.get("font_size_pt")
        if size and size > 0:
            self.editor.set_text_font_size(size)
            self.toolbar.set_font_size(size)

    # ═══════════════════════════════════════════════
    def _update_title(self):
        name = self.current_file.name if self.current_file else "بدون نام"
        star = " •" if self._dirty else ""
        self.setWindowTitle(f"{name}{star} — {__app_name__}")

    def _on_contents_changed(self):
        if self._suppress_dirty:
            return
        if not self._dirty:
            self._dirty = True
            self._update_title()
        self._update_stats()

    def _set_clean(self):
        self._dirty = False
        self._update_title()

    def _confirm_discard(self) -> bool:
        if not self._dirty:
            return True
        ans = QMessageBox.question(
            self,
            "تغییرات ذخیره‌نشده",
            "تغییرات ذخیره نشده است. ذخیره شود؟",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if ans == QMessageBox.StandardButton.Save:
            return self._save_document()
        if ans == QMessageBox.StandardButton.Discard:
            return True
        return False

    def _new_document(self):
        if not self._confirm_discard():
            return
        self._suppress_dirty = True
        try:
            self.editor.clear_content()
            self.current_file = None
            self._dirty = False
            self._update_title()
        finally:
            self._suppress_dirty = False
        self._update_stats()

    def _open_document(self):
        if not self._confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "باز کردن فیلم‌نامه",
            str(Path.home() / "Documents"),
            FILE_FILTER,
        )
        if not path:
            return
        try:
            doc = ScreenplayDocument.load(path)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"فایل باز نشد:\n{e}")
            return

        self._suppress_dirty = True
        try:
            self.editor.set_blocks(doc.blocks)
            self.current_file = Path(path)
            self._dirty = False
            self._update_title()
        finally:
            self._suppress_dirty = False

        self._update_stats()

    def _save_document(self) -> bool:
        if self.current_file is None:
            return self._save_document_as()
        return self._write_to(self.current_file)

    def _save_document_as(self) -> bool:
        suggested_name = "فیلم‌نامه" + FILE_EXT
        suggested = str(Path.home() / "Documents" / suggested_name)
        path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره‌ی فیلم‌نامه", suggested, FILE_FILTER,
        )
        if not path:
            return False
        p = Path(path)
        if p.suffix != FILE_EXT:
            p = p.with_suffix(FILE_EXT)
        return self._write_to(p)

    def _write_to(self, path: Path) -> bool:
        try:
            doc = ScreenplayDocument()
            doc.blocks = self.editor.get_blocks()
            actual = doc.save(path)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"ذخیره نشد:\n{e}")
            return False
        self.current_file = actual
        self._set_clean()
        return True

    def closeEvent(self, event):
        if not self._confirm_discard():
            event.ignore()
        else:
            event.accept()

    # ═══════════════════════════════════════════════
    def _new_window(self):
        QMessageBox.information(
            self, "پنجره‌ی جدید",
            "این قابلیت در فازهای بعدی اضافه می‌شود.",
        )

    def _open_settings(self):
        QMessageBox.information(
            self, "تنظیمات",
            "این قابلیت در فازهای بعدی اضافه می‌شود.",
        )

    def _open_help(self):
        QMessageBox.information(
            self, "راهنما",
            "فیلم‌نویس — ویرایشگر فیلم‌نامه‌ی فارسی\n\n"
            "میان‌برها:\n"
            "  Ctrl+S — ذخیره\n"
            "  Ctrl+O — باز کردن\n"
            "  Ctrl+Shift+S — ذخیره به‌عنوان\n"
            "  Ctrl+1..6 — انتخاب المان\n"
            "  Ctrl+B / I / U — بولد / ایتالیک / زیرخط",
        )

    # ═══════════════════════════════════════════════
    def _apply_paper_margins(self, scale: float):
        self._paper_layout.setContentsMargins(
            int(mm_to_px(MARGIN_LEFT_MM) * scale),
            int(mm_to_px(MARGIN_TOP_MM) * scale),
            int(mm_to_px(MARGIN_RIGHT_MM) * scale),
            int(mm_to_px(MARGIN_BOTTOM_MM) * scale),
        )

    def _on_layout_changed(self):
        scale = self.editor.zoom_level_percent() / 100.0
        content_h = self.editor.document().size().height()
        total_h = int(content_h
                      + mm_to_px(MARGIN_TOP_MM) * scale
                      + mm_to_px(MARGIN_BOTTOM_MM) * scale
                      + 20)
        page_h = int(mm_to_px(PAGE_HEIGHT_MM) * scale)
        if total_h < page_h:
            total_h = page_h
        self._paper.setMinimumHeight(total_h)
        self._update_stats()

    def _on_zoom_changed(self, percent: int):
        scale = percent / 100.0
        self._paper.setFixedWidth(int(mm_to_px(PAGE_WIDTH_MM) * scale))
        self._apply_paper_margins(scale)
        self._paper.set_scale(scale)
        self._on_layout_changed()
        self.zoom_bar.set_zoom(percent)

    def _on_element_changed(self, elem_id: str):
        self.toolbar.set_active_element(elem_id)

    def _update_stats(self):
        text = self.editor.document().toPlainText()
        words = len([w for w in text.split() if w.strip()])

        blocks = self.editor.get_blocks()
        scenes = sum(1 for b in blocks if b.get("type") == "scene")
        chars = len({
            b["text"].strip()
            for b in blocks
            if b.get("type") == "character" and b.get("text", "").strip()
        })

        current_page = self.editor.current_page()
        total_pages = self.editor.total_pages()
        duration = total_pages

        self.counters.set_stats(words, scenes, chars,
                                current_page, total_pages, duration)

    def _open_font_dialog(self):
        dialog = FontPickerDialog(
            self.editor.get_text_font_family(),
            self.editor.get_text_font_size(),
            self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            family = dialog.selected_family()
            size = dialog.selected_size()
            if family:
                self.editor.set_text_font_family(family)
                self.settings["font_family_text"] = family
                self.toolbar.set_font_family(family)
            if size > 0:
                self.editor.set_text_font_size(size)
                self.settings["font_size_pt"] = size
                self.toolbar.set_font_size(size)
            save_settings(self.settings)
