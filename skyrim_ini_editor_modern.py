#!/usr/bin/env python3
"""Modern GUI wrapper for the Skyrim INI Editor.

This launcher provides a more modern, styled UI using ttk themes while
reusing the same core INI parsing and editing logic from `skyrim_ini_editor.py`.

This file is intentionally independent: you can launch it separately to
compare the modern UI to the classic one.
"""

import tkinter as tk
from tkinter import ttk

try:
    # Optional: use ttkbootstrap for a modern look (if installed)
    import ttkbootstrap as tb  # type: ignore
    HAS_BOOTSTRAP = True
except Exception:
    HAS_BOOTSTRAP = False

import sys

from skyrim_ini_editor import SkyrimINIEditor  # use existing full-featured editor


def main() -> None:
    """Launch the modern UI wrapper."""
    root = tk.Tk()

    # Apply a modern theme if available
    if HAS_BOOTSTRAP:
        tb.Style("superhero")
    else:
        if sys.version_info >= (3, 15):
            print(
                "Warning: Python 3.15+ has no prebuilt Pillow wheel, so ttkbootstrap may not be installable. "
                "The app will use the built-in ttk theme instead."
            )

        style = ttk.Style(root)
        for theme in ("clam", "alt", "default"):
            try:
                style.theme_use(theme)
                break
            except tk.TclError:
                continue
        style.configure("TButton", padding=6)
        style.configure("TLabel", padding=4)

    # Instantiate the existing editor—this keeps all functionality identical.
    SkyrimINIEditor(root)
    root.title("Skyrim INI Editor (Modern)")

    # Start the UI loop
    root.mainloop()


if __name__ == '__main__':
    main()
