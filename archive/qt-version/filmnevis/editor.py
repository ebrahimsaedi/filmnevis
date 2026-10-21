"""ویرایشگر متن فیلمنامه با RTL."""

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QPainter,
    QTextBlockFormat,
    QTextBlockUserData,
    QTextCharFormat,
    QTextCursor,
    QTextOption,
)
from PySide6.QtWidgets import QTextEdit

from filmnevis.constants import (
    ELEMENTS,
    ELEMENT_ORDER,
    FONT_FAMILY_TEXT,
    FONT_SIZE_PT,
    MARGIN_BOTTOM_MM,
    MARGIN_TOP_MM,
    PAGE_HEIGHT_MM,
    mm_to_px,
)


NBSP = "\u00a0"


class ElementBlockData(QTextBlockUserData):
    def __init__(self, elem_id: str):
        super().__init__()
        self.elem_id = elem_id


class FilmnevisEditor(QTextEdit):
    element_changed = Signal(str)
    zoom_changed = Signal(int)
    layout_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_element = "scene"
        self._text_family = FONT_FAMILY_TEXT
        self._text_size_pt = FONT_SIZE_PT
        self._zoom_percent = 100
        self._suppress_fix = False

        self.setLayoutDirection(Qt.RightToLeft)
        self.viewport().setLayoutDirection(Qt.RightToLeft)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setFrameStyle(QTextEdit.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCursorWidth(1)

        self.document().setDocumentMargin(0)
        self._update_default_font()

        opt = QTextOption()
        opt.setTextDirection(Qt.RightToLeft)
        opt.setAlignment(Qt.AlignRight)
        opt.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.document().setDefaultTextOption(opt)

        cursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.Start)
        self._apply_element_to_cursor(cursor, "scene")
        self._ensure_placeholder(self.document().firstBlock())

        self.cursorPositionChanged.connect(self._on_cursor_moved)
        self.document().contentsChanged.connect(self._on_contents_changed)

    # ═══════════════════════════════════════════════
    #  نمایش
    # ═══════════════════════════════════════════════
    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(80, self._initial_cursor)

    def _initial_cursor(self):
        block = self.document().firstBlock()
        if not block.isValid():
            return
        c = QTextCursor(block)
        c.movePosition(QTextCursor.EndOfBlock)
        self.setTextCursor(c)
        self.setFocus()
        self.viewport().update()

    # ═══════════════════════════════════════════════
    #  صفحه — محاسبه‌ی شماره
    # ═══════════════════════════════════════════════
    def _page_height_px(self) -> float:
        scale = self._zoom_percent / 100.0
        mm = PAGE_HEIGHT_MM - MARGIN_TOP_MM - MARGIN_BOTTOM_MM
        return mm_to_px(mm) * scale

    def total_pages(self) -> int:
        doc_h = self.document().size().height()
        page_h = self._page_height_px()
        if page_h <= 0:
            return 1
        return max(1, int(doc_h // page_h) + 1)

    def current_page(self) -> int:
        block = self.textCursor().block()
        if not block.isValid():
            return 1
        top = self.document().documentLayout().blockBoundingRect(block).top()
        page_h = self._page_height_px()
        if page_h <= 0:
            return 1
        return int(top // page_h) + 1

    # ═══════════════════════════════════════════════
    #  محتوای تغییر یافته
    # ═══════════════════════════════════════════════
    def _on_contents_changed(self):
        if self._suppress_fix:
            return
        QTimer.singleShot(0, self._after_content_change)

    def _after_content_change(self):
        if self._suppress_fix:
            return
        self._ensure_current_block_placeholder()
        self._auto_resize()
        self.layout_changed.emit()
        self.viewport().update()

    def _ensure_current_block_placeholder(self):
        if self._suppress_fix:
            return
        block = self.textCursor().block()
        if block.text() == "":
            self._suppress_fix = True
            try:
                self._ensure_placeholder(block)
                c = QTextCursor(block)
                c.movePosition(QTextCursor.EndOfBlock)
                self.setTextCursor(c)
            finally:
                self._suppress_fix = False

    def _auto_resize(self):
        """ارتفاع ادیتور رو با محتوا هماهنگ می‌کنه."""
        doc_h = self.document().size().height()
        new_h = int(doc_h) + 20
        if new_h < 1:
            new_h = 1
        if self.minimumHeight() != new_h:
            self.setMinimumHeight(new_h)

    # ═══════════════════════════════════════════════
    #  فونت
    # ═══════════════════════════════════════════════
    def _update_default_font(self):
        scale = self._zoom_percent / 100.0
        font = QFont(self._text_family)
        font.setPointSizeF(self._text_size_pt * scale)
        font.setStyleStrategy(QFont.PreferAntialias)
        self.document().setDefaultFont(font)

    def set_text_font_family(self, family: str):
        self._text_family = family
        self._update_default_font()
        self._retag_all_blocks()
        self.viewport().update()

    def set_text_font_size(self, pt: int):
        self._text_size_pt = max(8, min(72, pt))
        self._update_default_font()
        self._retag_all_blocks()
        self.viewport().update()

    def get_text_font_family(self) -> str:
        return self._text_family

    def get_text_font_size(self) -> int:
        return self._text_size_pt

    # ═══════════════════════════════════════════════
    #  فرمت‌ها
    # ═══════════════════════════════════════════════
    def _block_format_for(self, elem_id: str, block_number: int,
                          prev_elem: str = None) -> QTextBlockFormat:
        cfg = ELEMENTS[elem_id]
        scale = self._zoom_percent / 100.0

        fmt = QTextBlockFormat()
        fmt.setLayoutDirection(Qt.RightToLeft)

        if "push_left_mm" in cfg:
            right_mm = cfg["push_left_mm"]
        else:
            right_mm = cfg["indent_right_mm"]

        fmt.setRightMargin(mm_to_px(right_mm) * scale)
        fmt.setLeftMargin(0)

        if cfg["align"] == "left":
            fmt.setAlignment(Qt.AlignLeft | Qt.AlignAbsolute)
        else:
            fmt.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)

        if block_number == 0:
            fmt.setTopMargin(0)
        else:
            if elem_id == "action" and prev_elem in ("scene", "action"):
                fmt.setTopMargin(0)
            else:
                fmt.setTopMargin(int(cfg["space_before_px"] * scale))
        fmt.setBottomMargin(0)

        return fmt

    def _char_format_for(self, elem_id: str) -> QTextCharFormat:
        cfg = ELEMENTS[elem_id]
        scale = self._zoom_percent / 100.0

        fmt = QTextCharFormat()
        fmt.setFontFamily(self._text_family)
        fmt.setFontPointSize(self._text_size_pt * scale)
        fmt.setFontWeight(QFont.Bold if cfg["bold"] else QFont.Normal)
        fmt.setLayoutDirection(Qt.RightToLeft)
        return fmt

    def _format_all_chars(self, block, char_fmt: QTextCharFormat):
        c = QTextCursor(block)
        c.select(QTextCursor.BlockUnderCursor)
        c.setCharFormat(char_fmt)
        c2 = QTextCursor(block)
        c2.setBlockCharFormat(char_fmt)

    def _ensure_placeholder(self, block):
        if block.text() == "":
            c = QTextCursor(block)
            c.movePosition(QTextCursor.EndOfBlock)
            c.insertText(NBSP)

    # ═══════════════════════════════════════════════
    #  اعمال المان
    # ═══════════════════════════════════════════════
    def _prev_elem_of(self, block) -> str:
        prev = block.previous()
        if prev.isValid():
            return self._elem_of_block(prev)
        return None

    def _apply_element_to_cursor(self, cursor: QTextCursor, elem_id: str):
        if elem_id not in ELEMENTS:
            return
        block = cursor.block()
        block_num = block.blockNumber()
        prev_elem = self._prev_elem_of(block)

        block_fmt = self._block_format_for(elem_id, block_num, prev_elem)
        char_fmt = self._char_format_for(elem_id)

        cursor.beginEditBlock()
        try:
            c = QTextCursor(block)
            c.setBlockFormat(block_fmt)
            self._format_all_chars(block, char_fmt)
            block.setUserData(ElementBlockData(elem_id))
        finally:
            cursor.endEditBlock()

    def _retag_all_blocks(self):
        block = self.document().firstBlock()
        cursor = self.textCursor()
        cursor.beginEditBlock()
        try:
            prev_elem = None
            while block.isValid():
                elem = self._elem_of_block(block) or "action"
                block_num = block.blockNumber()
                c = QTextCursor(block)
                c.setBlockFormat(self._block_format_for(elem, block_num, prev_elem))
                self._format_all_chars(block, self._char_format_for(elem))
                prev_elem = elem
                block = block.next()
        finally:
            cursor.endEditBlock()
        self._auto_resize()
        self.layout_changed.emit()

    def _elem_of_block(self, block) -> str:
        data = block.userData()
        if isinstance(data, ElementBlockData):
            return data.elem_id
        return None

    # ═══════════════════════════════════════════════
    #  API
    # ═══════════════════════════════════════════════
    def current_element(self) -> str:
        return self._current_element

    def set_current_element(self, elem_id: str):
        if elem_id not in ELEMENTS:
            return

        cursor = self.textCursor()

        if cursor.hasSelection():
            self._apply_to_selection(elem_id)
            self.element_changed.emit(elem_id)
            return

        self._current_element = elem_id
        block_num = cursor.blockNumber()
        block_before = self.document().findBlockByNumber(block_num)
        was_empty = block_before.text() in ("", NBSP)

        self._apply_element_to_cursor(cursor, elem_id)

        if elem_id == "parenthetical" and was_empty:
            self._suppress_fix = True
            try:
                blk = self.document().findBlockByNumber(block_num)
                c_del = QTextCursor(blk)
                c_del.movePosition(QTextCursor.StartOfBlock)
                c_del.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                c_del.removeSelectedText()

                blk = self.document().findBlockByNumber(block_num)
                c_ins = QTextCursor(blk)
                c_ins.insertText("()")

                blk = self.document().findBlockByNumber(block_num)
                c_fmt = QTextCursor(blk)
                c_fmt.select(QTextCursor.BlockUnderCursor)
                c_fmt.setCharFormat(self._char_format_for(elem_id))
            finally:
                self._suppress_fix = False

            QTimer.singleShot(20, lambda: self._cursor_into_paren(block_num))

        elif elem_id == "transition" and was_empty:
            self._suppress_fix = True
            try:
                blk = self.document().findBlockByNumber(block_num)
                c_del = QTextCursor(blk)
                c_del.movePosition(QTextCursor.StartOfBlock)
                c_del.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                c_del.removeSelectedText()

                blk = self.document().findBlockByNumber(block_num)
                c_ins = QTextCursor(blk)
                c_ins.insertText(":")

                blk = self.document().findBlockByNumber(block_num)
                c_fmt = QTextCursor(blk)
                c_fmt.select(QTextCursor.BlockUnderCursor)
                c_fmt.setCharFormat(self._char_format_for(elem_id))
            finally:
                self._suppress_fix = False

            QTimer.singleShot(20, lambda: self._cursor_before_colon(block_num))
        else:
            QTimer.singleShot(20, lambda: self._place_cursor(block_num))

        self.element_changed.emit(elem_id)

    def _cursor_into_paren(self, block_number: int):
        block = self.document().findBlockByNumber(block_number)
        if not block.isValid():
            return
        if block.text() == "()":
            c = QTextCursor(self.document())
            c.setPosition(block.position() + 1)
            self.setTextCursor(c)
            self.ensureCursorVisible()
            self.setFocus()
            self.viewport().update()
        else:
            c = QTextCursor(block)
            c.movePosition(QTextCursor.EndOfBlock)
            self.setTextCursor(c)
            self.setFocus()

    def _cursor_before_colon(self, block_number: int):
        block = self.document().findBlockByNumber(block_number)
        if not block.isValid():
            return
        if block.text() == ":":
            c = QTextCursor(self.document())
            c.setPosition(block.position())
            self.setTextCursor(c)
            self.ensureCursorVisible()
            self.setFocus()
            self.viewport().update()
        else:
            c = QTextCursor(block)
            c.movePosition(QTextCursor.EndOfBlock)
            self.setTextCursor(c)
            self.setFocus()

    def _place_cursor(self, block_number: int):
        block = self.document().findBlockByNumber(block_number)
        if not block.isValid():
            return
        c = QTextCursor(block)
        c.movePosition(QTextCursor.EndOfBlock)
        self.setTextCursor(c)
        self.ensureCursorVisible()
        self.setFocus()
        self.viewport().update()

    def _apply_to_selection(self, elem_id: str):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        block = self.document().findBlock(start)
        last_block = self.document().findBlock(end)

        self._suppress_fix = True
        work = QTextCursor(self.document())
        work.beginEditBlock()
        try:
            prev_elem = self._prev_elem_of(block)
            while True:
                block_num = block.blockNumber()
                c = QTextCursor(block)
                c.setBlockFormat(self._block_format_for(elem_id, block_num, prev_elem))
                self._format_all_chars(block, self._char_format_for(elem_id))
                block.setUserData(ElementBlockData(elem_id))
                prev_elem = elem_id

                if block == last_block:
                    break
                block = block.next()
                if not block.isValid():
                    break
        finally:
            work.endEditBlock()
            self._suppress_fix = False

        self._current_element = elem_id
        self._auto_resize()
        self.layout_changed.emit()

    # ═══════════════════════════════════════════════
    #  کیبورد
    # ═══════════════════════════════════════════════
    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() & Qt.ControlModifier:
            key = event.key()
            if Qt.Key_1 <= key <= Qt.Key_6:
                idx = key - Qt.Key_1
                if idx < len(ELEMENT_ORDER):
                    self.set_current_element(ELEMENT_ORDER[idx])
                    return

        if event.key() == Qt.Key_Backspace:
            cursor = self.textCursor()
            if not cursor.hasSelection():
                block = cursor.block()
                txt = block.text()
                only_placeholder = txt in ("", NBSP, ":")
                at_end = (cursor.positionInBlock() >= len(txt))

                if only_placeholder and at_end and block.blockNumber() > 0:
                    self._suppress_fix = True
                    try:
                        c = QTextCursor(block)
                        c.movePosition(QTextCursor.StartOfBlock)
                        c.deletePreviousChar()
                    finally:
                        self._suppress_fix = False
                    return
                if only_placeholder and block.blockNumber() == 0:
                    return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._handle_enter()
            return

        if event.text() == "(":
            cursor = self.textCursor()
            if not cursor.hasSelection() and cursor.block().text() in ("", NBSP):
                self.set_current_element("parenthetical")
                return

        super().keyPressEvent(event)

    def _handle_enter(self):
        cursor = self.textCursor()
        current = self._elem_of_block(cursor.block()) or self._current_element
        block = cursor.block()
        is_empty = block.text() in ("", NBSP)

        if current == "parenthetical":
            cursor.movePosition(QTextCursor.EndOfBlock)
            self.setTextCursor(cursor)
            next_elem = "dialogue"
        elif current == "transition":
            cursor.movePosition(QTextCursor.EndOfBlock)
            self.setTextCursor(cursor)
            next_elem = "scene"
        elif is_empty:
            next_elem = current
        else:
            next_elem = ELEMENTS[current]["next"]

        cursor = self.textCursor()
        self._suppress_fix = True
        cursor.beginEditBlock()
        try:
            cursor.insertBlock()
            new_block = cursor.block()
            new_block_num = new_block.blockNumber()
            block_fmt = self._block_format_for(next_elem, new_block_num, current)
            char_fmt = self._char_format_for(next_elem)
            new_block.setUserData(ElementBlockData(next_elem))
            c2 = QTextCursor(new_block)
            c2.setBlockFormat(block_fmt)
            c2.setBlockCharFormat(char_fmt)
            c2.setCharFormat(char_fmt)
            c3 = QTextCursor(new_block)
            c3.movePosition(QTextCursor.EndOfBlock)
            c3.insertText(NBSP)
        finally:
            cursor.endEditBlock()
            self._suppress_fix = False

        QTimer.singleShot(10, lambda: self._place_cursor(new_block_num))

        self._current_element = next_elem
        self.element_changed.emit(next_elem)

    def _on_cursor_moved(self):
        elem = self._elem_of_block(self.textCursor().block())
        if elem and elem != self._current_element:
            self._current_element = elem
            self.element_changed.emit(elem)
        self.layout_changed.emit()

    # ═══════════════════════════════════════════════
    #  ذخیره و بارگذاری
    # ═══════════════════════════════════════════════
    def get_blocks(self) -> list[dict]:
        """همه‌ی بلوک‌ها را به‌صورت لیست dict برمی‌گرداند."""
        blocks = []
        block = self.document().firstBlock()
        while block.isValid():
            elem = self._elem_of_block(block) or "action"
            raw = block.text()
            # حذف NBSP و کاراکترهای مخفی از ابتدا/انتها
            text = raw.replace(NBSP, "").strip()
            blocks.append({"type": elem, "text": text})
            block = block.next()
        return blocks

    def set_blocks(self, blocks: list[dict]) -> None:
        """متن را از لیست بلوک‌ها بارگذاری می‌کند."""
        if not blocks:
            blocks = [{"type": "scene", "text": ""}]

        self._suppress_fix = True
        try:
            self.clear()

            for i, blk in enumerate(blocks):
                elem_id = blk.get("type", "action")
                if elem_id not in ELEMENTS:
                    elem_id = "action"
                text = blk.get("text", "")

                # موقعیت: بلوک اول یا بلوک جدید
                if i == 0:
                    cursor = QTextCursor(self.document().firstBlock())
                else:
                    cursor = QTextCursor(self.document())
                    cursor.movePosition(QTextCursor.End)
                    cursor.insertBlock()

                new_block = cursor.block()
                block_fmt = self._block_format_for(elem_id, i, None)
                char_fmt = self._char_format_for(elem_id)
                new_block.setUserData(ElementBlockData(elem_id))

                c2 = QTextCursor(new_block)
                c2.setBlockFormat(block_fmt)
                c2.setBlockCharFormat(char_fmt)
                c2.setCharFormat(char_fmt)

                # درج متن
                c3 = QTextCursor(new_block)
                c3.movePosition(QTextCursor.EndOfBlock)
                c3.insertText(text if text else NBSP)

                # فرمت روی کاراکترها
                c4 = QTextCursor(new_block)
                c4.select(QTextCursor.BlockUnderCursor)
                c4.setCharFormat(char_fmt)

            # مکان‌نما در ابتدای سند
            first = self.document().firstBlock()
            c = QTextCursor(first)
            c.movePosition(QTextCursor.EndOfBlock)
            self.setTextCursor(c)
        finally:
            self._suppress_fix = False

        self._auto_resize()
        self.layout_changed.emit()
        self.viewport().update()

    def clear_content(self) -> None:
        """کل متن را پاک می‌کند و یک بلوک خالی صحنه می‌سازد."""
        self.set_blocks([{"type": "scene", "text": ""}])

    # ═══════════════════════════════════════════════
    #  زوم
    # ═══════════════════════════════════════════════
    def zoom_in(self):
        self.set_zoom(self._zoom_percent + 10)

    def zoom_out(self):
        self.set_zoom(self._zoom_percent - 10)

    def zoom_reset(self):
        self.set_zoom(100)

    def set_zoom(self, percent: int):
        percent = max(25, min(300, percent))
        self._zoom_percent = percent
        self._update_default_font()
        self._retag_all_blocks()
        self.zoom_changed.emit(percent)

    def zoom_level_percent(self) -> int:
        return self._zoom_percent
