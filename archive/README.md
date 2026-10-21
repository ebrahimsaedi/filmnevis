# The R&D Archive: Prototypes & Post-Mortems 🧪

This directory contains two early prototypes of **Filmnevis**. They are kept here to document the learning process, architectural trade-offs, and the technical bottlenecks encountered while building a rich-text screenwriting editor.

While these prototypes are **not production-ready** and were ultimately abandoned, they serve as valuable case studies for developers interested in UI framework limitations regarding complex block formatting.

---

## 1. The GTK4 Prototype (`/gtk-version`)
- **Tech Stack:** Python, GTK4, Libadwaita.
- **Objective:** Create a native, GNOME-style editor with deep integration into the Linux desktop environment.

### ⚠️ Why it was abandoned (Technical Post-Mortem)
GTK is an incredible framework for standard UI, but `Gtk.TextBuffer` is not designed for complex, block-level rich text formatting. 
- **The Hack:** To achieve different margins and indents for dialogues vs. action lines, the app had to rebuild all text tags on every single keystroke. 
- **The Consequences:** This caused severe performance lag on longer texts. Additionally, keeping empty lines visible required inserting hidden ZWNJ/Zero-width characters, which resulted in cursor navigation glitches and scroll-jumping bugs.

---

## 2. The Qt Prototype (`/qt-version`)
- **Tech Stack:** Python, PySide6 (Qt for Python).
- **Objective:** Leverage Qt's powerful `QTextDocument` framework to achieve a much better architecture.

### ⚠️ Why it was archived (Technical Post-Mortem)
This prototype was a massive architectural leap forward. By using `QTextBlockUserData`, it successfully mapped screenplay elements to paragraphs without hacking the text buffer.
- **The Bottleneck:** Implementing **true pagination** (where text automatically flows from the bottom of one physical A4 page to the top of the next) proved incredibly difficult using `QTextBlockBoundingRect`. The prototype was essentially one infinitely long A4 page.
- **Performance:** Retagging all blocks on zoom or font-size changes caused significant lag on large documents.

---

### 💡 How this shapes the Final Version
The upcoming Final Version of Filmnevis builds heavily upon the Qt prototype. It resolves the pagination issues by implementing a custom `QAbstractTextDocumentLayout` and optimizes performance by only formatting the visible viewport rather than the entire document.

---
## 🚀 How to run the prototypes
If you are interested in exploring these early stages, you can run them locally.

### Running the Qt Prototype (Recommended)
```bash
cd qt-version
pip install PySide6
python main.py
