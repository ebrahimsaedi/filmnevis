"""مدل سند فیلمنامه و ذخیره/باز کردن JSON."""

import json
from datetime import datetime
from pathlib import Path


SCHEMA_VERSION = 1
FILE_EXT = ".filmnevis"


class ScreenplayDocument:
    """مدل داده‌ی سند فیلمنامه."""

    def __init__(self):
        now = datetime.now().isoformat(timespec="seconds")
        self.meta = {
            "title": "",
            "author": "",
            "type": "screenplay",
            "created": now,
            "modified": now,
        }
        self.blocks: list[dict] = []

    @property
    def title(self) -> str:
        return self.meta.get("title") or "بدون عنوان"

    def update_modified(self) -> None:
        self.meta["modified"] = datetime.now().isoformat(timespec="seconds")

    def to_dict(self) -> dict:
        return {
            "version": SCHEMA_VERSION,
            "meta": self.meta,
            "blocks": self.blocks,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScreenplayDocument":
        doc = cls()
        # version = data.get("version", 1)
        # در آینده: مهاجرت از نسخه‌های قدیمی
        meta = data.get("meta")
        if isinstance(meta, dict):
            doc.meta.update(meta)
        blocks = data.get("blocks")
        if isinstance(blocks, list):
            doc.blocks = blocks
        return doc

    def save(self, path) -> Path:
        self.update_modified()
        p = Path(path)
        if p.suffix != FILE_EXT:
            p = p.with_suffix(FILE_EXT)
        p.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return p

    @classmethod
    def load(cls, path) -> "ScreenplayDocument":
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("فرمت فایل نامعتبر است")
        return cls.from_dict(data)
