"""راه‌اندازی Gtk.Application."""

from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk, Adw, Gdk, Gio, GLib  # noqa: E402

from filmnevis import __app_id__  # noqa: E402
from filmnevis.settings import load_settings, save_settings  # noqa: E402
from filmnevis.window import FilmnevisWindow  # noqa: E402
from filmnevis.new_document import NewDocumentDialog  # noqa: E402
from filmnevis.constants import ELEMENT_ORDER  # noqa: E402


_SCHEME_MAP = {
    "light":   Adw.ColorScheme.FORCE_LIGHT,
    "dark":    Adw.ColorScheme.FORCE_DARK,
    "default": Adw.ColorScheme.DEFAULT,
}


class FilmnevisApp(Adw.Application):
    """برنامه‌ی اصلی فیلمنویس."""

    def __init__(self):
        super().__init__(
            application_id=__app_id__,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.settings = load_settings()
        self._setup_actions()
        self._apply_saved_scheme()

    def do_activate(self):
        self._load_css()
        win = self.props.active_window
        if not win:
            win = FilmnevisWindow(application=self)
            win.present()
            dialog = NewDocumentDialog(win, self._on_document_type_chosen)
            dialog.present()
        else:
            win.present()

    def _on_document_type_chosen(self, doc_type: str):
        win = self.props.active_window
        if win:
            win.set_document_type(doc_type)
            # فوکوس رو به ویرایشگر برگردان
            def _refocus():
                win.editor.get_textview().grab_focus()
                return False
            GLib.idle_add(_refocus)

    # ── اکشن‌ها ──
    def _setup_actions(self):
        # تم
        scheme_action = Gio.SimpleAction.new_stateful(
            "color-scheme",
            GLib.VariantType.new("s"),
            GLib.Variant.new_string(self.settings.get("color_scheme", "default")),
        )
        scheme_action.connect("activate", self._on_color_scheme)
        self.add_action(scheme_action)

        # خروج
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])

        # درباره
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

        # زوم
        zoom_in = Gio.SimpleAction.new("zoom-in", None)
        zoom_in.connect("activate", lambda *_: self._zoom(0.1))
        self.add_action(zoom_in)
        self.set_accels_for_action("app.zoom-in", ["<Ctrl>equal", "<Ctrl>plus"])

        zoom_out = Gio.SimpleAction.new("zoom-out", None)
        zoom_out.connect("activate", lambda *_: self._zoom(-0.1))
        self.add_action(zoom_out)
        self.set_accels_for_action("app.zoom-out", ["<Ctrl>minus"])

        zoom_reset = Gio.SimpleAction.new("zoom-reset", None)
        zoom_reset.connect("activate", lambda *_: self._zoom_reset())
        self.add_action(zoom_reset)
        self.set_accels_for_action("app.zoom-reset", ["<Ctrl>0"])

        # انتخاب المان با Ctrl+1..6
        for i, elem_id in enumerate(ELEMENT_ORDER, start=1):
            action_name = f"element-{elem_id}"
            act = Gio.SimpleAction.new(action_name, None)
            act.connect("activate", self._on_element_shortcut, elem_id)
            self.add_action(act)
            self.set_accels_for_action(f"app.{action_name}", [f"<Ctrl>{i}"])

    def _on_element_shortcut(self, action, param, elem_id):
        win = self.props.active_window
        if win is not None:
            win.select_element(elem_id)

    def _zoom(self, delta):
        win = self.props.active_window
        if win:
            win._do_zoom(delta)

    def _zoom_reset(self):
        win = self.props.active_window
        if win:
            win._do_zoom_reset()

    def _on_color_scheme(self, action, param):
        scheme_str = param.get_string()
        action.set_state(param)
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(_SCHEME_MAP.get(
            scheme_str, Adw.ColorScheme.DEFAULT
        ))
        self.settings["color_scheme"] = scheme_str
        save_settings(self.settings)

    def _apply_saved_scheme(self):
        style_manager = Adw.StyleManager.get_default()
        scheme_str = self.settings.get("color_scheme", "default")
        style_manager.set_color_scheme(_SCHEME_MAP.get(
            scheme_str, Adw.ColorScheme.DEFAULT
        ))

    def _on_about(self, *_):
        win = self.props.active_window
        about = Adw.AboutWindow(
            transient_for=win,
            application_name="فیلمنویس",
            application_icon="com.ebrahimsaedi.Filmnevis",
            version="0.2.0",
            developer_name="ابراهیم ساعدی",
            license_type=Gtk.License.GPL_3_0,
            comments="ویرایشگر فیلمنامه‌ی فارسی با قالب استاندارد",
        )
        about.set_direction(Gtk.TextDirection.RTL)
        about.present()

    def _load_css(self):
        css_path = Path(__file__).resolve().parent / "style.css"
        if not css_path.is_file():
            return
        provider = Gtk.CssProvider()
        provider.load_from_path(str(css_path))
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display, provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )


def main():
    app = FilmnevisApp()
    return app.run(None)
