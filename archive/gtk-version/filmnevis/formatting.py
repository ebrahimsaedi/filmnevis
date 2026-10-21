"""قالب‌بندی المان‌های فیلمنامه — مدیریت TextTagها."""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # noqa: E402

from filmnevis.constants import (  # noqa: E402
    ELEMENTS,
    ELEMENT_ORDER,
    LINE_SPACING_BELOW_PX,
    mm_to_px,
    FONT_FAMILY,
    FONT_SIZE_PT,
)


BASE_FONT_TAG = "base_font"
NO_SPACE_TAG = "no_space_above"


class ElementFormatter:
    """مدیریت تگ‌های TextTag برای المان‌های فیلمنامه."""

    def __init__(self, buffer: Gtk.TextBuffer):
        self.buffer = buffer
        self._zoom_level = 1.0
        self._build_tags()

    # ── ساخت تگ‌ها ──
    def _build_tags(self):
        """ترتیب مهم است: no_space باید آخر ساخته شود تا priority بالاتری
        نسبت به المان‌ها داشته باشد (در GTK4، تگ‌های جدیدتر اولویت
        بالاتری دارند)."""
        # ۱. تگ فونت پایه
        self._ensure_base_font_tag()
        # ۲. تگ‌های المان‌ها
        for eid in ELEMENT_ORDER:
            self._ensure_element_tag(eid)
        # ۳. تگ no_space (آخرین ساخته → بالاترین priority)
        self._ensure_no_space_tag()

    def _ensure_base_font_tag(self):
        tag = self.buffer.get_tag_table().lookup(BASE_FONT_TAG)
        if tag is None:
            tag = self.buffer.create_tag(BASE_FONT_TAG)
        tag.set_property("family", FONT_FAMILY)
        tag.set_property(
            "size-points",
            max(1, int(round(FONT_SIZE_PT * self._zoom_level))),
        )

    def _ensure_no_space_tag(self):
        tag = self.buffer.get_tag_table().lookup(NO_SPACE_TAG)
        if tag is None:
            tag = self.buffer.create_tag(NO_SPACE_TAG)
        tag.set_property("pixels-above-lines", 0)

    def _ensure_element_tag(self, elem_id: str):
        cfg = ELEMENTS[elem_id]
        tag = self.buffer.get_tag_table().lookup(elem_id)
        if tag is None:
            tag = self.buffer.create_tag(elem_id)

        indent_mm = cfg.get("push_left_mm", cfg["indent_right_mm"])
        indent_px = int(round(mm_to_px(indent_mm) * self._zoom_level))
        tag.set_property("right-margin", indent_px)
        tag.set_property("left-margin", 0)

        before = int(round(cfg.get("space_before_px", 0) * self._zoom_level))
        after = int(round(LINE_SPACING_BELOW_PX * self._zoom_level))
        tag.set_property("pixels-above-lines", before)
        tag.set_property("pixels-below-lines", after)

    # ── اعمال ──
    def apply_base_font(self):
        tag = self.buffer.get_tag_table().lookup(BASE_FONT_TAG)
        if tag is not None:
            self.buffer.apply_tag(
                tag,
                self.buffer.get_start_iter(),
                self.buffer.get_end_iter(),
            )

    def apply_element_tag(self, elem_id: str,
                          start: Gtk.TextIter, end: Gtk.TextIter):
        tag = self.buffer.get_tag_table().lookup(elem_id)
        if tag is None:
            return
        s, e = start.copy(), end.copy()
        if s.equal(e):
            if not e.forward_char():
                if not s.backward_char():
                    return
        self.buffer.apply_tag(tag, s, e)

    def remove_all_element_tags(self,
                                start: Gtk.TextIter, end: Gtk.TextIter):
        for eid in ELEMENT_ORDER:
            t = self.buffer.get_tag_table().lookup(eid)
            if t is not None:
                self.buffer.remove_tag(t, start, end)
        ns = self.buffer.get_tag_table().lookup(NO_SPACE_TAG)
        if ns is not None:
            self.buffer.remove_tag(ns, start, end)

    def apply_no_space(self, start: Gtk.TextIter, end: Gtk.TextIter):
        tag = self.buffer.get_tag_table().lookup(NO_SPACE_TAG)
        if tag is not None:
            self.buffer.apply_tag(tag, start, end)

    # ── خواندن ──
    def get_element_at(self, it: Gtk.TextIter):
        for tag in it.get_tags():
            name = tag.get_property("name")
            if name in ELEMENT_ORDER:
                return name
        return None

    # ── زوم ──
    def set_zoom(self, level: float):
        self._zoom_level = level
        self._build_tags()
        self.apply_base_font()
