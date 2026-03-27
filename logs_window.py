"""
Access log viewer window.
Displays the full access history with colour-coded decisions.
"""

import tkinter as tk
from tkinter import ttk

from config import (
    BG_DARK, BG_CARD, BG_PANEL,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER,
    TEXT_PRI, TEXT_SEC
)


class LogsWindow:
    COLUMNS = [
        "Timestamp", "Name", "Role", "Decision",
        "Measured Height", "Registered Height", "Confidence"
    ]

    def __init__(self, parent, db):
        self.db = db
        win = tk.Toplevel(parent)
        win.title("Access Logs")
        win.configure(bg=BG_DARK)
        win.geometry("960x500")
        self._build(win)

    def _build(self, win):
        tk.Label(win, text="ACCESS LOG",
                 font=("Courier", 13, "bold"), fg=ACCENT_BLUE,
                 bg=BG_DARK).pack(pady=10)

        frame = tk.Frame(win, bg=BG_DARK)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        style = ttk.Style()
        style.configure("Treeview",
                         background=BG_CARD, foreground=TEXT_PRI,
                         fieldbackground=BG_CARD, font=("Courier", 9))
        style.configure("Treeview.Heading",
                         background=BG_PANEL, foreground=ACCENT_BLUE,
                         font=("Courier", 9, "bold"))

        tree = ttk.Treeview(frame, columns=self.COLUMNS,
                             show="headings", height=24)
        for col in self.COLUMNS:
            tree.heading(col, text=col)
            tree.column(col, width=122, anchor=tk.CENTER)

        tree.tag_configure("GRANTED", foreground=ACCENT_GREEN)
        tree.tag_configure("DENIED",  foreground=ACCENT_RED)
        tree.tag_configure("VISITOR", foreground=ACCENT_AMBER)

        for row in reversed(self.db.get_logs()):
            dec = row.get("Decision", "")
            tree.insert("", tk.END,
                        values=[row.get(c, "—") for c in self.COLUMNS],
                        tags=(dec,))

        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
