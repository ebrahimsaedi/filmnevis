"""ویرایشگر — صفحه‌ی A4 با متن راست‌چین و قالب فیلمنامه."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk, Gdk, GLib  # noqa: E402

from filmnevis.constants import (  # noqa: E402
    PAGE_WIDTH_MM, PAGE_HEIGHT_MM,
    MARGIN_TOP_MM, MARGIN_BOTTOM_MM,
    MARGIN_LEFT_MM, MARGIN_RIGHT_MM,
    ELEMENTS, mm_to_px,
)
from filmnevis.formatting import ElementFormatter  # noqa: E402


ZWNJ = "\u200c"
INVISIBLE = "\u200b\u200c\u200d\u200e\u200f\ufeff"


def _strip_invisible(text: str) -> str:
    return "".join(c for c in text if c not in INVISIBLE)


def _line_start(buffer, line):
    _, it = buffer.get_iter_at_line_offset(line, 0)
    return it


def _line_end(buffer, line):
    _, it = buffer.get_iter_at_line_offset(line, 0)
    it.forward_to_line_end()
    return it


class FilmnevisEditor(Gtk.Box):
    """صفحه‌ی سفید A4 با حاشیه‌های استاندارد فیلمنامه."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # ── منبع حقیقت ──
        # نگاشت خط → المان. تنها مرجع برنامه.
        self._line_elements: dict[int, str] = {0: "scene"}
        self._current_element = "scene"
        self._zoom_level = 1.0
        self._suppress_change = False
        self._on_element_changed_cb = None

        self._saved_scroll = None
        self._lock_until_us = 0
        self._restoring_scroll = False

        # ── اسکرول ──
        self._scroller = Gtk.ScrolledWindow()
        self._scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self._scroller.set_vexpand(True)
        self._scroller.set_hexpand(True)
        self.append(self._scroller)

        self._vadj = self._scroller.get_vadjustment()
        self._vadj.connect("value-changed", self._on_scroll_value_changed)

        wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        wrapper.add_css_class("page-wrapper")
        wrapper.set_halign(Gtk.Align.CENTER)
        wrapper.set_valign(Gtk.Align.START)
        wrapper.set_margin_top(20)
        wrapper.set_margin_bottom(20)
        self._scroller.set_child(wrapper)

        self._page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._page.add_css_class("page")
        self._page.set_direction(Gtk.TextDirection.RTL)
        self._page.set_size_request(
            mm_to_px(PAGE_WIDTH_MM), mm_to_px(PAGE_HEIGHT_MM)
        )
        self._page.set_halign(Gtk.Align.CENTER)
        self._page.set_valign(Gtk.Align.START)
        wrapper.append(self._page)

        self._text_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._text_area.add_css_class("text-area")
        self._text_area.set_direction(Gtk.TextDirection.RTL)
        self._text_area.set_margin_top(mm_to_px(MARGIN_TOP_MM))
        self._text_area.set_margin_bottom(mm_to_px(MARGIN_BOTTOM_MM))
        self._text_area.set_margin_start(mm_to_px(MARGIN_RIGHT_MM))
        self._text_area.set_margin_end(mm_to_px(MARGIN_LEFT_MM))
        self._page.append(self._text_area)

        # ── ویرایشگر ──
        self.textview = Gtk.TextView()
        self.textview.add_css_class("screenplay-text")
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.set_direction(Gtk.TextDirection.RTL)
        self.textview.set_left_margin(0)
        self.textview.set_right_margin(0)
        self.textview.set_top_margin(0)
        self.textview.set_bottom_margin(0)
        self.textview.set_monospace(False)
        self.textview.set_overwrite(False)
        self.textview.set_accepts_tab(False)
        self.textview.set_vexpand(True)
        self._text_area.append(self.textview)

        self.buffer = self.textview.get_buffer()
        self.buffer.set_enable_undo(True)
        self._formatter = ElementFormatter(self.buffer)

        # مقدار اولیه: یک ZWNJ در خط 0
        self._suppress_change = True
        try:
            self.buffer.insert(self.buffer.get_start_iter(), ZWNJ)
            self.buffer.place_cursor(self.buffer.get_iter_at_offset(1))
        finally:
            self._suppress_change = False

        self._rebuild_all()

        self.buffer.connect("changed", self._on_buffer_changed)
        self.buffer.connect("mark-set", self._on_mark_set)

        key = Gtk.EventControllerKey.new()
        key.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        key.connect("key-pressed", self._on_key_pressed)
        self.textview.add_controller(key)

        cl = Gtk.GestureClick.new()
        cl.set_button(1)
        cl.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        cl.connect("pressed", lambda *_: self._start_scroll_lock(400_000))
        self.textview.add_controller(cl)

        cr = Gtk.GestureClick.new()
        cr.set_button(3)
        cr.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        cr.connect("pressed", lambda *_: self._start_scroll_lock(2_000_000))
        self.textview.add_controller(cr)

        GLib.timeout_add(150, self._initial_focus)

    def _initial_focus(self):
        if not self.textview.get_mapped():
            return True
        self.buffer.place_cursor(self.buffer.get_end_iter())
        self.textview.grab_focus()
        return False

    # ═══════════════════════════════════════════════
    #  REBUILD — بازسازی کامل از دیکشنری
    # ═══════════════════════════════════════════════
    def _rebuild_all(self):
        """همه‌ی تگ‌ها را از _line_elements بازسازی می‌کند."""
        buffer = self.buffer
        total = buffer.get_line_count()

        # ۱. اطمینان از اینکه دیکشنری همه‌ی خطوط را دارد
        for line in range(total):
            if line not in self._line_elements:
                self._line_elements[line] = self._current_element

        # ۲. حذف کلیدهای اضافی (خطوطی که دیگر وجود ندارند)
        for line in list(self._line_elements.keys()):
            if line >= total:
                del self._line_elements[line]

        # ۳. ذخیره‌ی مکان‌نمای فعلی
        cursor_iter = buffer.get_iter_at_mark(buffer.get_insert())
        cursor_offset = cursor_iter.get_offset()

        # ۴. حذف همه‌ی تگ‌های المان از کل بافر
        self._formatter.remove_all_element_tags(
            buffer.get_start_iter(), buffer.get_end_iter()
        )

        # ۵. برای هر خط: ZWNJ در صورت خالی بودن، auto-()، اعمال تگ
        cursor_should_move_to = None
        for line in range(total):
            ls = _line_start(buffer, line)
            le = _line_end(buffer, line)

            # خط خالی → ZWNJ
            if ls.equal(le):
                buffer.insert(ls, ZWNJ)
                ls = _line_start(buffer, line)
                le = _line_end(buffer, line)

            elem = self._line_elements[line]

            # parenthetical خالی → ()
            if elem == "parenthetical":
                para = buffer.get_text(ls, le, False)
                if _strip_invisible(para).strip() == "":
                    # حذف محتوای فعلی
                    buffer.delete(ls, le)
                    ins = _line_start(buffer, line)
                    ins_off = ins.get_offset()
                    buffer.insert(ins, "()")
                    # اگر مکان‌نما در همین خط بود، وسط پرانتز بگذار
                    if cursor_iter.get_line() == line:
                        cursor_should_move_to = ins_off + 1
                    ls = _line_start(buffer, line)
                    le = _line_end(buffer, line)

            # اعمال تگ
            self._formatter.apply_element_tag(elem, ls, le)
            if line == 0:
                self._formatter.apply_no_space(ls, le)

        # ۶. فونت پایه
        self._formatter.apply_base_font()

        # ۷. بازگرداندن مکان‌نما
        if cursor_should_move_to is not None:
            try:
                buffer.place_cursor(
                    buffer.get_iter_at_offset(cursor_should_move_to)
                )
            except Exception:
                pass
        else:
            try:
                new_cursor = buffer.get_iter_at_offset(cursor_offset)
                buffer.place_cursor(new_cursor)
            except Exception:
                pass

    # ═══════════════════════════════════════════════
    #  BUFFER CHANGED
    # ═══════════════════════════════════════════════
    def _on_buffer_changed(self, buffer):
        if self._suppress_change:
            return
        self._suppress_change = True
        try:
            # شیفت دیکشنری بر اساس تغییر تعداد خطوط
            self._resync_dict_with_buffer()
            self._rebuild_all()
        finally:
            self._suppress_change = False
        GLib.idle_add(self._finalize)

    def _resync_dict_with_buffer(self):
        """اگر تعداد خطوط تغییر کرده، دیکشنری را با بافر همگام کن.

        نکته: چون این تابع تنها در تغییرات خارجی (paste، backspace روی
        مرز خط) صدا زده می‌شود، فرض می‌کنیم تغییرات در محل مکان‌نمای
        فعلی رخ داده‌اند.
        """
        buffer = self.buffer
        total = buffer.get_line_count()

        # اگر تعداد خطوط با بزرگ‌ترین کلید + ۱ یکی نیست، خطوطی حذف شده‌اند
        if not self._line_elements:
            return

        max_key = max(self._line_elements.keys())
        if max_key + 1 == total:
            return  # تعداد خطوط با دیکشنری می‌خواند

        # تغییر تعداد خطوط — شیفت در محل مکان‌نما
        cursor = buffer.get_iter_at_mark(buffer.get_insert())
        cursor_line = cursor.get_line()

        if total > max_key + 1:
            # خطوط اضافه شده
            diff = total - (max_key + 1)
            new_dict = {}
            for ln, el in self._line_elements.items():
                if ln >= cursor_line:
                    new_dict[ln + diff] = el
                else:
                    new_dict[ln] = el
            self._line_elements = new_dict
        else:
            # خطوط حذف شده
            diff = (max_key + 1) - total
            new_dict = {}
            for ln, el in self._line_elements.items():
                if ln < cursor_line:
                    new_dict[ln] = el
                elif ln > cursor_line + diff:
                    new_dict[ln - diff] = el
                # elif cursor_line <= ln <= cursor_line + diff: خط حذف شده
            self._line_elements = new_dict

    def _finalize(self):
        self.textview.queue_resize()
        self.textview.queue_draw()
        return False

    # ═══════════════════════════════════════════════
    #  KEYBOARD
    # ═══════════════════════════════════════════════
    def _on_key_pressed(self, controller, keyval, keycode, state):
        if state & Gdk.ModifierType.CONTROL_MASK:
            if keyval in (Gdk.KEY_c, Gdk.KEY_x, Gdk.KEY_a,
                          Gdk.KEY_C, Gdk.KEY_X, Gdk.KEY_A):
                self._start_scroll_lock(800_000)
                return False

        if keyval == Gdk.KEY_parenleft:
            cursor = self.buffer.get_iter_at_mark(self.buffer.get_insert())
            ls = cursor.copy(); ls.set_line_offset(0)
            le = cursor.copy(); le.forward_to_line_end()
            txt = _strip_invisible(
                self.buffer.get_text(ls, le, False)
            ).strip()
            if txt == "":
                self.set_current_element("parenthetical")
                return True
            return False

        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self._handle_enter()
            return True

        return False

    def _handle_enter(self):
        buffer = self.buffer
        self._suppress_change = True
        try:
            cursor = buffer.get_iter_at_mark(buffer.get_insert())
            line = cursor.get_line()

            current = self._line_elements.get(line, self._current_element)

            # آیا این خط خالی است؟
            ls = _line_start(buffer, line)
            le = _line_end(buffer, line)
            txt = buffer.get_text(ls, le, False)
            empty = (_strip_invisible(txt).strip() == "")

            # تعیین المان بعدی
            if current == "parenthetical":
                next_elem = "dialogue"
            elif empty:
                next_elem = current
            else:
                next_elem = ELEMENTS[current]["next"]

            # درج \n در انتهای خط
            insert_offset = le.get_offset()
            buffer.insert(buffer.get_iter_at_offset(insert_offset), "\n")

            # شیفت دیکشنری
            new_dict = {}
            for ln, el in self._line_elements.items():
                if ln > line:
                    new_dict[ln + 1] = el
                else:
                    new_dict[ln] = el
            new_dict[line + 1] = next_elem
            self._line_elements = new_dict
            self._current_element = next_elem

            # بازسازی کامل
            self._rebuild_all()

            # مکان‌نما در ابتدای خط جدید
            try:
                buffer.place_cursor(_line_start(buffer, line + 1))
            except Exception:
                pass
        finally:
            self._suppress_change = False

        if self._on_element_changed_cb:
            self._on_element_changed_cb(self._current_element)
        GLib.idle_add(self._finalize)

    # ═══════════════════════════════════════════════
    #  SET ELEMENT
    # ═══════════════════════════════════════════════
    def set_current_element(self, elem_id):
        if elem_id not in ELEMENTS:
            return
        changed = elem_id != self._current_element
        self._current_element = elem_id

        buffer = self.buffer
        self._suppress_change = True
        try:
            cursor = buffer.get_iter_at_mark(buffer.get_insert())
            line = cursor.get_line()

            self._line_elements[line] = elem_id
            self._rebuild_all()
        finally:
            self._suppress_change = False

        if changed and self._on_element_changed_cb:
            self._on_element_changed_cb(elem_id)
        GLib.idle_add(self._finalize)

    def get_current_element(self):
        return self._current_element

    def set_on_element_changed(self, cb):
        self._on_element_changed_cb = cb

    def _on_mark_set(self, buffer, location, mark):
        if mark.get_name() != "insert":
            return
        if self._suppress_change:
            return
        line = location.get_line()
        elem = self._line_elements.get(line)
        if elem and elem != self._current_element:
            self._current_element = elem
            if self._on_element_changed_cb:
                self._on_element_changed_cb(elem)

    # ═══════════════════════════════════════════════
    #  SCROLL LOCK
    # ═══════════════════════════════════════════════
    def _start_scroll_lock(self, duration_us=800_000):
        self._saved_scroll = self._vadj.get_value()
        self._lock_until_us = GLib.get_monotonic_time() + duration_us
        for d in (10, 30, 60, 120, 250, 500, 800, 1200, 1800):
            if d * 1000 <= duration_us:
                GLib.timeout_add(d, self._force_scroll)

    def _force_scroll(self):
        if self._saved_scroll is not None:
            self._restoring_scroll = True
            self._vadj.set_value(self._saved_scroll)
            self._restoring_scroll = False
        return False

    def _on_scroll_value_changed(self, adj):
        if self._restoring_scroll:
            return
        if self._saved_scroll is None:
            return
        if GLib.get_monotonic_time() >= self._lock_until_us:
            self._saved_scroll = None
            return
        if abs(adj.get_value() - self._saved_scroll) > 1.0:
            self._restoring_scroll = True
            adj.set_value(self._saved_scroll)
            self._restoring_scroll = False

    # ═══════════════════════════════════════════════
    #  ZOOM
    # ═══════════════════════════════════════════════
    def zoom(self, delta):
        self._zoom_level = max(0.25, min(3.0, self._zoom_level + delta))
        self._apply_zoom()

    def zoom_reset(self):
        self._zoom_level = 1.0
        self._apply_zoom()

    def get_zoom_level(self):
        return int(round(self._zoom_level * 100))

    def _apply_zoom(self):
        scale = self._zoom_level
        saved = self._vadj.get_value()

        self._formatter.set_zoom(scale)

        self._page.set_size_request(
            int(round(mm_to_px(PAGE_WIDTH_MM) * scale)),
            int(round(mm_to_px(PAGE_HEIGHT_MM) * scale)),
        )

        self._text_area.set_margin_top(
            int(round(mm_to_px(MARGIN_TOP_MM) * scale)))
        self._text_area.set_margin_bottom(
            int(round(mm_to_px(MARGIN_BOTTOM_MM) * scale)))
        self._text_area.set_margin_start(
            int(round(mm_to_px(MARGIN_RIGHT_MM) * scale)))
        self._text_area.set_margin_end(
            int(round(mm_to_px(MARGIN_LEFT_MM) * scale)))

        self._suppress_change = True
        try:
            self._rebuild_all()
        finally:
            self._suppress_change = False

        def _restore():
            self._restoring_scroll = True
            self._vadj.set_value(saved)
            self._restoring_scroll = False
            return False
        GLib.idle_add(_restore)

    # ═══════════════════════════════════════════════
    #  API
    # ═══════════════════════════════════════════════
    def get_buffer(self):
        return self.buffer

    def get_textview(self):
        return self.textview
