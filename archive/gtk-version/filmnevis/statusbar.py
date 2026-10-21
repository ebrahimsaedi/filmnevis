"""نوار وضعیت پایین پنجره."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # noqa: E402


def _to_persian_digits(value) -> str:
    """تبدیل عدد لاتین به رقم فارسی با جداکننده‌ی هزارگان."""
    if isinstance(value, float):
        s = f"{value:.0f}"
    else:
        s = f"{value:,}".replace(",", "٬")
    trans = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return s.translate(trans)


class FilmnevisStatusBar(Gtk.Box):
    """نوار پایین — شمارنده‌ها در راست، دکمه‌های زوم در چپ."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.add_css_class("statusbar")
        self.set_direction(Gtk.TextDirection.RTL)
        self.set_halign(Gtk.Align.FILL)
        self.set_hexpand(True)

        self._on_zoom_in = None
        self._on_zoom_out = None
        self._on_zoom_reset = None

        # ── شمارنده‌ها (راست) ──
        self.lbl_words = Gtk.Label()
        self.lbl_chars = Gtk.Label()
        self.lbl_element = Gtk.Label()
        self.lbl_page = Gtk.Label()

        for lbl in (self.lbl_words, self.lbl_chars,
                    self.lbl_element, self.lbl_page):
            self.append(lbl)

        # ── فاصله‌ی کش‌دار (وسط) ──
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        self.append(spacer)

        # ── دکمه‌های زوم (چپ) ──
        self.append(self._build_zoom_box())

        self.update(word_count=0, char_count=0,
                    element_label="صحنه", page=1, total_pages=1)
        self.set_zoom_level(100)

    # ── ساخت دکمه‌های زوم ──
    def _build_zoom_box(self) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        # ترتیب عددی برای همه آشناست — چپ‌به‌راست نگه می‌داریم
        box.set_direction(Gtk.TextDirection.LTR)

        btn_out = Gtk.Button(label="−")
        btn_out.add_css_class("flat")
        btn_out.add_css_class("zoom-btn")
        btn_out.set_tooltip_text("کوچک‌نمایی")
        btn_out.connect("clicked", self._on_zoom_out_clicked)
        box.append(btn_out)

        self.btn_zoom = Gtk.Button()
        self.btn_zoom.add_css_class("flat")
        self.btn_zoom.add_css_class("zoom-btn")
        self.btn_zoom.set_tooltip_text("بازگشت به ۱۰۰٪")
        self.btn_zoom.connect("clicked", self._on_zoom_reset_clicked)
        box.append(self.btn_zoom)

        btn_in = Gtk.Button(label="+")
        btn_in.add_css_class("flat")
        btn_in.add_css_class("zoom-btn")
        btn_in.set_tooltip_text("بزرگ‌نمایی")
        btn_in.connect("clicked", self._on_zoom_in_clicked)
        box.append(btn_in)

        return box

    # ── اتصال callbackها از پنجره ──
    def set_on_zoom_in(self, cb):
        self._on_zoom_in = cb

    def set_on_zoom_out(self, cb):
        self._on_zoom_out = cb

    def set_on_zoom_reset(self, cb):
        self._on_zoom_reset = cb

    def set_zoom_level(self, percent: int):
        """متن وسط دکمه‌ها را با درصد جدید به‌روز می‌کند."""
        self.btn_zoom.set_label(f"{_to_persian_digits(percent)}٪")

    # ── رویدادها ──
    def _on_zoom_in_clicked(self, *_):
        if self._on_zoom_in:
            self._on_zoom_in()

    def _on_zoom_out_clicked(self, *_):
        if self._on_zoom_out:
            self._on_zoom_out()

    def _on_zoom_reset_clicked(self, *_):
        if self._on_zoom_reset:
            self._on_zoom_reset()

    # ── شمارنده‌ها ──
    def update(self, word_count: int, char_count: int,
               element_label: str, page: int, total_pages: int):
        self.lbl_words.set_text(f"کلمات: {_to_persian_digits(word_count)}")
        self.lbl_chars.set_text(f"نویسه: {_to_persian_digits(char_count)}")
        self.lbl_element.set_text(f"المان: {element_label}")
        self.lbl_page.set_text(
            f"صفحه: {_to_persian_digits(page)} از {_to_persian_digits(total_pages)}"
        )

    def attach_buffer(self, buffer: Gtk.TextBuffer):
        buffer.connect("changed", self._on_buffer_changed)

    def _on_buffer_changed(self, buffer: Gtk.TextBuffer):
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        text = buffer.get_text(start, end, False)

        char_count = len(text)
        word_count = len([w for w in text.split() if w.strip()])

        self.lbl_words.set_text(f"کلمات: {_to_persian_digits(word_count)}")
        self.lbl_chars.set_text(f"نویسه: {_to_persian_digits(char_count)}")
