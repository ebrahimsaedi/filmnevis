"""دیالوگ انتخاب نوع سند در شروع."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw  # noqa: E402


_OPTIONS = [
    ("screenplay", "فیلمنامه",
     "با قالب استاندارد: صحنه، توصیف، شخصیت، دیالوگ، گذار"),
    ("prose", "متن معمولی",
     "برای نوشتن اوت‌لاین، لاگ‌لاین، سیناپسیس، تریتمنت و هر متن دیگر"),
]


class NewDocumentDialog(Adw.MessageDialog):
    """دیالوگ انتخاب نوع سند — فیلمنامه یا متن معمولی."""

    def __init__(self, parent, on_select):
        super().__init__(
            transient_for=parent,
            heading="چه می‌خواهی بنویسی؟",
            body="نوع سند تعیین می‌کند چه قالبی روی متن اعمال شود.",
        )
        self.set_direction(Gtk.TextDirection.RTL)
        self._on_select = on_select
        self._radios: dict[str, Gtk.CheckButton] = {}

        self.add_response("cancel", "انصراف")
        self.add_response("create", "شروع")
        self.set_response_appearance("create", Adw.ResponseAppearance.SUGGESTED)
        self.set_default_response("create")
        self.set_close_response("cancel")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_direction(Gtk.TextDirection.RTL)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        group = None
        for key, label, desc in _OPTIONS:
            row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            row.set_direction(Gtk.TextDirection.RTL)

            rb = Gtk.CheckButton(label=label)
            rb.set_direction(Gtk.TextDirection.RTL)
            if group is None:
                group = rb
                rb.set_active(True)
            else:
                rb.set_group(group)
            self._radios[key] = rb
            row.append(rb)

            lbl = Gtk.Label(label=desc)
            lbl.set_xalign(0.0)
            lbl.set_wrap(True)
            lbl.add_css_class("dim-label")
            lbl.set_margin_start(28)
            row.append(lbl)

            box.append(row)

        self.set_extra_child(box)
        self.connect("response", self._on_response)

    def _on_response(self, dialog, response):
        if response == "create":
            for key, rb in self._radios.items():
                if rb.get_active():
                    self._on_select(key)
                    break
        dialog.destroy()
