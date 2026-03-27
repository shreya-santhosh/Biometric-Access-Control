"""
Enrollment window UI for registering new users into the biometric system.
"""

import tkinter as tk
from tkinter import messagebox

from config import (
    BG_DARK, BG_PANEL, ACCENT_BLUE, ACCENT_GREEN,
    ACCENT_AMBER, ACCENT_RED, TEXT_PRI, TEXT_SEC
)


class EnrollWindow:
    def __init__(self, parent, db, engine, app):
        self.db      = db
        self.engine  = engine
        self.app     = app
        self._enrolled = False

        self.win = tk.Toplevel(parent)
        self.win.title("Enroll User")
        self.win.configure(bg=BG_DARK)
        self.win.geometry("460x580")
        self.win.resizable(False, False)

        self._build()

    def _build(self):
        tk.Label(self.win, text="ENROLL NEW USER",
                 font=("Courier", 13, "bold"), fg=ACCENT_BLUE,
                 bg=BG_DARK).pack(pady=12)

        self.entries = {}
        for lbl, key in [
            ("User ID",                  "id"),
            ("Full Name",                "name"),
            ("Role  ( ADMIN / EMPLOYEE )","role"),
            ("Registered Height  ( cm )", "height"),
        ]:
            tk.Label(self.win, text=lbl, font=("Arial", 10),
                     fg=TEXT_SEC, bg=BG_DARK, anchor=tk.W
                     ).pack(fill=tk.X, padx=22, pady=(10, 0))
            e = tk.Entry(self.win, font=("Courier", 11),
                         bg=BG_PANEL, fg=TEXT_PRI,
                         insertbackground=TEXT_PRI, bd=0)
            e.pack(fill=tk.X, padx=22, ipady=6)
            self.entries[key] = e

        self.cap_status = tk.Label(
            self.win, text="No face captured yet",
            font=("Courier", 10), fg=ACCENT_AMBER, bg=BG_DARK)
        self.cap_status.pack(pady=14)

        bs = {"font": ("Courier", 10, "bold"), "bd": 0, "pady": 8, "cursor": "hand2"}
        tk.Button(self.win, text="📸  CAPTURE FACE",
                  bg=ACCENT_BLUE, fg="white",
                  command=self._capture, **bs).pack(fill=tk.X, padx=22, pady=3)
        tk.Button(self.win, text="✓  SAVE & ENROLL",
                  bg=ACCENT_GREEN, fg="white",
                  command=self._save, **bs).pack(fill=tk.X, padx=22, pady=3)

    def _capture(self):
        frm = self.app.frame
        if frm is None:
            messagebox.showerror("Error", "Camera not ready.")
            return
        uid = self.entries["id"].get().strip()
        if not uid:
            messagebox.showerror("Error", "Enter a User ID first.")
            return

        self.cap_status.config(
            text="Processing… first run downloads VGG-Face model ~500 MB",
            fg=ACCENT_AMBER)
        self.win.update()

        ok = self.engine.enroll_face(frm, uid)
        if ok:
            self.cap_status.config(text="✓ Face captured and encoded",
                                   fg=ACCENT_GREEN)
            self._enrolled = True
            self.app._activity(f"Face captured for {uid}")
        else:
            self.cap_status.config(text="✗ No face detected — try again",
                                   fg=ACCENT_RED)

    def _save(self):
        uid   = self.entries["id"].get().strip()
        name  = self.entries["name"].get().strip()
        role  = self.entries["role"].get().strip().upper()
        h_str = self.entries["height"].get().strip()

        if not all([uid, name, role, h_str]):
            messagebox.showerror("Error", "Fill all fields.")
            return
        if role not in ("ADMIN", "EMPLOYEE"):
            messagebox.showerror("Error", "Role must be ADMIN or EMPLOYEE.")
            return
        if not self._enrolled:
            messagebox.showerror("Error", "Capture face first.")
            return
        try:
            height = float(h_str)
        except ValueError:
            messagebox.showerror("Error", "Height must be a number.")
            return

        self.db.add_user({
            "id": uid, "name": name, "role": role,
            "height_cm": height, "enrolled": True
        })
        messagebox.showinfo("Enrolled", f"{name} enrolled as {role}.")
        self.app._activity(f"Enrolled: {name} ({role}, {height} cm)")
        self.win.destroy()
