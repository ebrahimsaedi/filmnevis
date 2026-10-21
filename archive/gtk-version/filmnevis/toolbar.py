"""نوار ابزار افقی برای انتخاب المان‌های فیلمنامه."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # noqa: E402

from filmnevis.constants import ELEMENTS, ELEMENT_ORDER  # noqa: E402


class FilmnevisToolbar(Gtk.Box):
    """نوار المان‌ها — صحنه، توصیف، شخصیت، توضیح، دیالوگ، گذار."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.add_css_class("toolbar-strip")

        # راست‌به‌چپ — شروع از سمت راست
        self.set_direction(Gtk.TextDirection.RTL)
        self.set_halign(Gtk.Align.FILL)
        self.set_hexpand(True)
        self.set_can_focus(False)

        self._buttons: dict[str, Gtk.ToggleButton] = {}
        self._on_select = None
        self._suppress_signal = False

        for elem_id in ELEMENT_ORDER:
            label = ELEMENTS[elem_id]["label_fa"]
            btn = Gtk.ToggleButton(label=label)
            btn.add_css_class("element-btn")
            # جلوگیری از پرش صفحه هنگام کلیک
            btn.set_can_focus(False)
            btn.set_focus_on_click(False)
            btn.connect("toggled", self._on_toggled, elem_id)
            self.append(btn)
            self._buttons[elem_id] = btn

        self._buttons["scene"].set_active(True)

    def set_on_select(self, callback):
        self._on_select = callback

    def set_active(self, elem_id: str):
        if elem_id not in self._buttons:
            return
        self._suppress_signal = True
        for eid, btn in self._buttons.items():
            btn.set_active(eid == elem_id)
        self._suppress_signal = False

    def _on_toggled(self, btn, elem_id):
        if self._suppress_signal:
            return
        if not btn.get_active():
            btn.set_active(True)
            return
        for eid, other in self._buttons.items():
            if eid != elem_id and other.get_active():
                self._suppress_signal = True
                other.set_active(False)
                self._suppress_signal = False
        if self._on_select:
            self._on_select(elem_id)
