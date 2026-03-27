"""
Main application UI and camera processing loop.
Orchestrates the biometric engine, database, and all UI windows.
"""

import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
import datetime
import warnings
warnings.filterwarnings("ignore")

from config import (
    OPTIMAL_DIST_MIN, OPTIMAL_DIST_MAX,
    BG_DARK, BG_CARD, BG_PANEL,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER,
    TEXT_PRI, TEXT_SEC
)
from database import DatabaseManager
from engine import BiometricEngine
from enroll_window import EnrollWindow
from logs_window import LogsWindow


class App:
    def __init__(self):
        self.db      = DatabaseManager()
        self.engine  = BiometricEngine(self.db)
        self.cap     = None
        self.running = False
        self.frame   = None
        self.state   = "IDLE"

        # Recognition cache — throttled to every 1.5 s to keep UI smooth
        self._last_recog = 0
        self._last_log   = 0
        self._uid  = None
        self._sim  = 0.0
        self._rbox = None

        self.root = tk.Tk()
        self.root.title("Biometric Access Control — Johnson Controls Security Products")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1280x780")

        self._build_ui()
        self._start_camera()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._build_camera_panel(body)
        self._build_right_panel(body)

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG_CARD, height=56)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="⬡  BIOMETRIC ACCESS CONTROL SYSTEM",
                 font=("Courier", 13, "bold"), fg=ACCENT_BLUE,
                 bg=BG_CARD).pack(side=tk.LEFT, padx=20, pady=14)

        self.clock_lbl = tk.Label(hdr, text="",
                                  font=("Courier", 10), fg=TEXT_SEC, bg=BG_CARD)
        self.clock_lbl.pack(side=tk.RIGHT, padx=20)

        tk.Label(hdr, text="Johnson Controls India  |  Security Products",
                 font=("Arial", 9), fg=TEXT_SEC,
                 bg=BG_CARD).pack(side=tk.RIGHT, padx=10)
        self._tick()

    def _build_camera_panel(self, parent):
        cam = tk.Frame(parent, bg=BG_CARD)
        cam.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        tk.Label(cam, text="LIVE FEED",
                 font=("Courier", 8, "bold"), fg=TEXT_SEC,
                 bg=BG_CARD).pack(pady=(6, 0))

        self.cam_lbl = tk.Label(cam, bg="black")
        self.cam_lbl.pack(padx=6, pady=6, fill=tk.BOTH, expand=True)

        self.status_lbl = tk.Label(cam, text="● INITIALIZING",
                                   font=("Courier", 10, "bold"),
                                   fg=ACCENT_AMBER, bg=BG_PANEL, pady=5)
        self.status_lbl.pack(fill=tk.X, padx=6, pady=(0, 6))

    def _build_right_panel(self, parent):
        rp = tk.Frame(parent, bg=BG_DARK, width=300)
        rp.pack(side=tk.RIGHT, fill=tk.Y)
        rp.pack_propagate(False)

        self._build_decision_card(rp)
        self._build_readings_card(rp)
        self._build_controls(rp)
        self._build_activity_log(rp)

    def _build_decision_card(self, parent):
        card = tk.Frame(parent, bg=BG_CARD, pady=10)
        card.pack(fill=tk.X, pady=(0, 6))

        tk.Label(card, text="ACCESS DECISION",
                 font=("Courier", 8, "bold"), fg=TEXT_SEC, bg=BG_CARD).pack()
        self.dec_lbl = tk.Label(card, text="STANDBY",
                                font=("Courier", 20, "bold"), fg=TEXT_SEC, bg=BG_CARD)
        self.dec_lbl.pack(pady=4)
        self.dec_icon = tk.Label(card, text="◉",
                                 font=("Arial", 32), fg=TEXT_SEC, bg=BG_CARD)
        self.dec_icon.pack()

    def _build_readings_card(self, parent):
        card = tk.Frame(parent, bg=BG_CARD, padx=12, pady=8)
        card.pack(fill=tk.X, pady=(0, 6))

        tk.Label(card, text="BIOMETRIC READINGS",
                 font=("Courier", 8, "bold"), fg=TEXT_SEC,
                 bg=BG_CARD).pack(anchor=tk.W, pady=(0, 4))

        self.rd = {}
        for label, key in [
            ("Identity",   "identity"),
            ("Role",       "role"),
            ("Face Match", "face"),
            ("Confidence", "conf"),
            ("Measured H", "mh"),
            ("Registered H","rh"),
            ("Distance",   "dist"),
        ]:
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=f"{label}:",
                     font=("Arial", 9), fg=TEXT_SEC, bg=BG_CARD,
                     width=13, anchor=tk.W).pack(side=tk.LEFT)
            v = tk.Label(row, text="—",
                         font=("Courier", 9, "bold"), fg=TEXT_PRI, bg=BG_CARD)
            v.pack(side=tk.LEFT)
            self.rd[key] = v

    def _build_controls(self, parent):
        ctrl = tk.Frame(parent, bg=BG_CARD, padx=12, pady=8)
        ctrl.pack(fill=tk.X, pady=(0, 6))

        tk.Label(ctrl, text="CONTROLS",
                 font=("Courier", 8, "bold"), fg=TEXT_SEC,
                 bg=BG_CARD).pack(anchor=tk.W, pady=(0, 4))

        bs = {"font": ("Courier", 10, "bold"), "bd": 0, "pady": 7, "cursor": "hand2"}
        tk.Button(ctrl, text="▶  START SCAN",
                  bg=ACCENT_BLUE, fg="white",
                  command=self.start_scan, **bs).pack(fill=tk.X, pady=2)
        tk.Button(ctrl, text="⚙  CALIBRATE",
                  bg=BG_PANEL, fg=TEXT_PRI,
                  command=self.calibrate, **bs).pack(fill=tk.X, pady=2)
        tk.Button(ctrl, text="👤  ENROLL USER",
                  bg=BG_PANEL, fg=TEXT_PRI,
                  command=self._enroll_win, **bs).pack(fill=tk.X, pady=2)
        tk.Button(ctrl, text="📋  VIEW LOGS",
                  bg=BG_PANEL, fg=TEXT_PRI,
                  command=self._logs_win, **bs).pack(fill=tk.X, pady=2)
        tk.Button(ctrl, text="■  STOP",
                  bg=ACCENT_RED, fg="white",
                  command=self.stop_scan, **bs).pack(fill=tk.X, pady=2)

    def _build_activity_log(self, parent):
        act = tk.Frame(parent, bg=BG_CARD, padx=10, pady=8)
        act.pack(fill=tk.BOTH, expand=True)

        tk.Label(act, text="ACTIVITY LOG",
                 font=("Courier", 8, "bold"), fg=TEXT_SEC,
                 bg=BG_CARD).pack(anchor=tk.W)

        self.act_txt = tk.Text(act, bg=BG_DARK, fg=TEXT_SEC,
                               font=("Courier", 8), bd=0,
                               state=tk.DISABLED, wrap=tk.WORD)
        self.act_txt.pack(fill=tk.BOTH, expand=True, pady=4)

    # ── Clock ─────────────────────────────────────────────────────────────────

    def _tick(self):
        self.clock_lbl.config(
            text=datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._tick)

    # ── UI Helpers ────────────────────────────────────────────────────────────

    def _rd(self, key, val, color=TEXT_PRI):
        if key in self.rd:
            self.rd[key].config(text=val, fg=color)

    def _set_decision(self, text):
        cfg = {
            "GRANTED":  (ACCENT_GREEN, "✓"),
            "ADMIN":    (ACCENT_GREEN, "✓"),
            "EMPLOYEE": (ACCENT_BLUE,  "✓"),
            "VISITOR":  (ACCENT_AMBER, "⚠"),
            "DENIED":   (ACCENT_RED,   "✗"),
            "SCANNING": (ACCENT_BLUE,  "◌"),
            "STANDBY":  (TEXT_SEC,     "◉"),
        }
        color, icon = cfg.get(text, (TEXT_SEC, "◉"))
        self.dec_lbl.config(text=text,  fg=color)
        self.dec_icon.config(text=icon, fg=color)

    def _status(self, msg, color=TEXT_SEC):
        self.status_lbl.config(text=msg, fg=color)

    def _activity(self, msg):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.act_txt.config(state=tk.NORMAL)
        self.act_txt.insert(tk.END, f"[{ts}] {msg}\n")
        self.act_txt.see(tk.END)
        self.act_txt.config(state=tk.DISABLED)

    def _overlay(self, f):
        h, w = f.shape[:2]
        L, t, c = 28, 2, (0, 80, 180)
        for x, y in [(0,0),(w-L,0),(0,h-L),(w-L,h-L)]:
            cv2.line(f, (x, y), (x+L, y), c, t)
            cv2.line(f, (x, y), (x, y+L), c, t)
        cx, cy = w//2, h//2
        cv2.line(f, (cx-12, cy), (cx+12, cy), c, 1)
        cv2.line(f, (cx, cy-12), (cx, cy+12), c, 1)

    # ── Camera ────────────────────────────────────────────────────────────────

    def _start_camera(self):
        self.cap     = cv2.VideoCapture(0)
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()
        self._status("● CAMERA READY — Calibrate then Start Scan", ACCENT_GREEN)
        self._activity("System online.")

    def _loop(self):
        while self.running:
            ret, frm = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue
            self.frame = frm.copy()
            display    = frm.copy()

            if self.state == "SCANNING":
                display = self._process(display)
            elif self.state == "CALIBRATING":
                cv2.putText(display, "CALIBRATING — Stand 61 cm away",
                            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                            (0, 255, 255), 2)

            self._overlay(display)
            img   = cv2.cvtColor(cv2.resize(display, (740, 520)),
                                 cv2.COLOR_BGR2RGB)
            photo = ImageTk.PhotoImage(Image.fromarray(img))
            self.cam_lbl.config(image=photo)
            self.cam_lbl.image = photo
            time.sleep(0.03)

    # ── Processing Pipeline ───────────────────────────────────────────────────

    def _process(self, frm):
        dist, fbox = self.engine.distance(frm)

        if dist is None:
            cv2.putText(frm, "NO FACE DETECTED", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return frm

        # Distance indicator
        in_range = OPTIMAL_DIST_MIN <= dist <= OPTIMAL_DIST_MAX
        color = (0, 255, 100) if in_range else (0, 165, 255)
        if fbox:
            x, y, w, h = fbox
            cv2.rectangle(frm, (x, y), (x+w, y+h), color, 2)
        self.root.after(0, self._rd, "dist", f"{dist:.1f} cm",
                        ACCENT_GREEN if in_range else ACCENT_AMBER)

        if not in_range:
            guide = "STEP BACK" if dist < OPTIMAL_DIST_MIN else "MOVE CLOSER"
            cv2.putText(frm, guide,
                        (frm.shape[1]//2 - 80, frm.shape[0]//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 2)
            return frm

        # Throttled face recognition
        now = time.time()
        if now - self._last_recog > 1.5:
            self._last_recog = now
            self._uid, self._sim, self._rbox = self.engine.recognize(frm)

        if self._rbox:
            x, y, w, h = self._rbox
            cv2.rectangle(frm, (x, y), (x+w, y+h), (0, 200, 255), 2)

        # Height estimation
        h_cm, frm = self.engine.height(frm)

        # Access decision
        if self._uid and h_cm:
            decision, user = self.engine.decide(self._uid, h_cm)
            name    = user["name"]     if user else "Unknown"
            reg_h   = user["height_cm"] if user else "N/A"
            granted = decision in ("ADMIN", "EMPLOYEE")
            disp    = "GRANTED" if granted else decision

            self.root.after(0, self._rd, "identity", name,
                            ACCENT_GREEN if self._uid not in (None, "UNKNOWN") else ACCENT_RED)
            self.root.after(0, self._rd, "role", decision,
                            ACCENT_GREEN if granted else ACCENT_RED)
            self.root.after(0, self._rd, "face",
                            "✓ MATCH" if self._uid not in (None, "UNKNOWN") else "✗ UNKNOWN",
                            ACCENT_GREEN if self._uid not in (None, "UNKNOWN") else ACCENT_RED)
            self.root.after(0, self._rd, "conf", f"{self._sim*100:.1f}%", TEXT_PRI)
            self.root.after(0, self._rd, "mh",   f"{h_cm:.1f} cm",        TEXT_PRI)
            self.root.after(0, self._rd, "rh",
                            f"{reg_h} cm" if reg_h != "N/A" else "—", TEXT_SEC)
            self.root.after(0, self._set_decision, disp)

            cv2.putText(frm, f"{name}  [{decision}]",
                        (10, frm.shape[0] - 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                        (0, 255, 100) if granted else (0, 0, 255), 2)

            if now - self._last_log > 3:
                self._last_log = now
                self.db.log(name, decision, disp, h_cm, reg_h, self._sim)
                self.root.after(0, self._activity, f"{name} → {disp}")

        return frm

    # ── Controls ──────────────────────────────────────────────────────────────

    def start_scan(self):
        if self.engine.focal_length is None:
            messagebox.showwarning(
                "Calibration Required",
                "Please calibrate first.\nClick CALIBRATE and follow the instructions.")
            return
        self.state = "SCANNING"
        self._status("● SCANNING ACTIVE — Multi-modal verification running",
                     ACCENT_GREEN)
        self._set_decision("SCANNING")
        self._activity("Scan started.")

    def stop_scan(self):
        self.state = "IDLE"
        self._status("● IDLE", TEXT_SEC)
        self._set_decision("STANDBY")
        for k in self.rd:
            self._rd(k, "—", TEXT_SEC)

    def calibrate(self):
        self.state = "CALIBRATING"
        self._status("● CALIBRATING", ACCENT_AMBER)
        messagebox.showinfo(
            "Calibration",
            "Stand exactly 61 cm (2 feet) from the camera.\n"
            "Look directly at the camera.\nClick OK when ready.")
        if self.frame is not None and self.engine.calibrate(self.frame):
            self._status("● CALIBRATION COMPLETE", ACCENT_GREEN)
            self._activity(f"Calibrated. FL={self.engine.focal_length:.1f}")
            messagebox.showinfo("Done", "Calibration successful!")
        else:
            self._status("● CALIBRATION FAILED", ACCENT_RED)
            messagebox.showerror("Failed", "No face detected. Try again.")
        self.state = "IDLE"

    def _enroll_win(self):
        EnrollWindow(self.root, self.db, self.engine, self)

    def _logs_win(self):
        LogsWindow(self.root, self.db)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.mainloop()

    def _close(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.destroy()
