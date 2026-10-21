"""پنجره‌ی اصلی فیلمنویس."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio  # noqa: E402

from filmnevis import __app_name__  # noqa: E402
from filmnevis.editor import FilmnevisEditor  # noqa: E402
from filmnevis.statusbar import FilmnevisStatusBar  # noqa: E402
from filmnevis.toolbar import FilmnevisToolbar  # noqa: E402
from filmnevis.constants import ELEMENTS  # noqa: E402


PROSE_TYPES = {"prose"}


class FilmnevisWindow(Adw.ApplicationWindow):
    """پنجره‌ی اصلی — نوار بالا، ویرایشگر، نوار وضعیت."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title(__app_name__)
        self.set_default_size(1100, 850)
        self.set_direction(Gtk.TextDirection.RTL)

        self.document_type = "screenplay"

        # ── نوار عنوان ──
        header = Adw.HeaderBar()
        header.set_direction(Gtk.TextDirection.RTL)

        theme_button = self._create_theme_button()
        header.pack_start(theme_button)

        main_menu = self._create_main_menu()
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(main_menu)
        menu_button.set_tooltip_text("منوی اصلی")
        header.pack_end(menu_button)

        # ── ساختار عمودی ──
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.set_direction(Gtk.TextDirection.RTL)

        self.toolbar = FilmnevisToolbar()
        root.append(self.toolbar)

        self.editor = FilmnevisEditor()
        self.editor.set_vexpand(True)
        root.append(self.editor)

        self.statusbar = FilmnevisStatusBar()
        root.append(self.statusbar)

        # اتصال‌ها
        self.statusbar.attach_buffer(self.editor.get_buffer())
        self.toolbar.set_on_select(self.select_element)
        self.editor.set_on_element_changed(self._on_editor_element_changed)

        # دکمه‌های زوم
        self.statusbar.set_on_zoom_in(lambda: self._do_zoom(0.1))
        self.statusbar.set_on_zoom_out(lambda: self._do_zoom(-0.1))
        self.statusbar.set_on_zoom_reset(self._do_zoom_reset)

        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)
        toolbar_view.set_content(root)
        self.set_content(toolbar_view)

    # ── انتخاب المان ──
    def select_element(self, elem_id: str):
        """انتخاب المان از نوار ابزار یا میان‌بر."""
        self.editor.set_current_element(elem_id)

    def _on_editor_element_changed(self, elem_id: str):
        """ادیتور المان را عوض کرد — نوار و وضعیت را هماهنگ کن."""
        self.toolbar.set_active(elem_id)
        if self.document_type in PROSE_TYPES:
            return
        label = ELEMENTS[elem_id]["label_fa"]
        self.statusbar.update(
            word_count=self._current_word_count(),
            char_count=self._current_char_count(),
            element_label=label,
            page=1, total_pages=1,
        )

    # ── زوم ──
    def _do_zoom(self, delta: float):
        self.editor.zoom(delta)
        self.statusbar.set_zoom_level(self.editor.get_zoom_level())

    def _do_zoom_reset(self):
        self.editor.zoom_reset()
        self.statusbar.set_zoom_level(self.editor.get_zoom_level())

    # ── نوع سند ──
    def set_document_type(self, doc_type: str):
        self.document_type = doc_type
        is_prose = doc_type in PROSE_TYPES

        self.toolbar.set_visible(not is_prose)

        label = "متن معمولی" if is_prose else "فیلمنامه"

        self.set_title(f"{label} — {__app_name__}")
        self.statusbar.update(
            word_count=self._current_word_count(),
            char_count=self._current_char_count(),
            element_label="—" if is_prose else "صحنه",
            page=1, total_pages=1,
        )

    # ── دکمه‌ی تم ──
    def _create_theme_button(self) -> Gtk.MenuButton:
        menu = Gio.Menu()
        menu.append("روشن", "app.color-scheme::light")
        menu.append("تاریک", "app.color-scheme::dark")
        menu.append("بر اساس سیستم", "app.color-scheme::default")

        button = Gtk.MenuButton()
        button.set_icon_name("display-brightness-symbolic")
        button.set_menu_model(menu)
        button.set_tooltip_text("ظاهر برنامه")
        return button

    # ── منوی اصلی ──
    def _create_main_menu(self) -> Gio.Menu:
        menu = Gio.Menu()
        menu.append("درباره‌ی فیلمنویس", "app.about")
        menu.append("خروج", "app.quit")
        return menu

    # ── شمارنده‌ها ──
    def _current_word_count(self) -> int:
        buf = self.editor.get_buffer()
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
        return len([w for w in text.split() if w.strip()])

    def _current_char_count(self) -> int:
        buf = self.editor.get_buffer()
        return len(buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False))
