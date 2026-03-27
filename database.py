"""
Database management for the Biometric Access Control System.
Handles user records, face embeddings, and access logs.
"""

import json
import os
import csv
import datetime
import numpy as np

from config import DATABASE_FILE, LOG_FILE, EMBEDDINGS_FILE, ENROLLED_FACES_DIR


class DatabaseManager:
    def __init__(self):
        for d in ["database", "logs", ENROLLED_FACES_DIR]:
            os.makedirs(d, exist_ok=True)
        self._init_db()
        self._init_log()
        self.embeddings = self._load_embeddings()

    # ── Initialisation ────────────────────────────────────────────────────────

    def _init_db(self):
        if not os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "w") as f:
                json.dump({"users": []}, f, indent=2)

    def _init_log(self):
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", newline="") as f:
                csv.writer(f).writerow([
                    "Timestamp", "Name", "Role", "Decision",
                    "Measured Height", "Registered Height", "Confidence"
                ])

    def _load_embeddings(self):
        if os.path.exists(EMBEDDINGS_FILE):
            with open(EMBEDDINGS_FILE) as f:
                return json.load(f)
        return {}

    def _save_embeddings(self):
        with open(EMBEDDINGS_FILE, "w") as f:
            json.dump(self.embeddings, f)

    # ── User Management ───────────────────────────────────────────────────────

    def get_users(self):
        with open(DATABASE_FILE) as f:
            return json.load(f)["users"]

    def get_user(self, user_id):
        return next((u for u in self.get_users() if u["id"] == user_id), None)

    def add_user(self, data):
        with open(DATABASE_FILE) as f:
            db = json.load(f)
        db["users"].append(data)
        with open(DATABASE_FILE, "w") as f:
            json.dump(db, f, indent=2)

    def update_user(self, user_id, updates):
        with open(DATABASE_FILE) as f:
            db = json.load(f)
        for u in db["users"]:
            if u["id"] == user_id:
                u.update(updates)
        with open(DATABASE_FILE, "w") as f:
            json.dump(db, f, indent=2)

    # ── Face Embeddings ───────────────────────────────────────────────────────

    def save_embedding(self, user_id, embedding):
        self.embeddings[user_id] = embedding
        self._save_embeddings()
        self.update_user(user_id, {"enrolled": True})

    # ── Access Logging ────────────────────────────────────────────────────────

    def log(self, name, role, decision, measured_h, reg_h, confidence):
        with open(LOG_FILE, "a", newline="") as f:
            csv.writer(f).writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name, role, decision,
                f"{measured_h:.1f}" if measured_h else "N/A",
                reg_h or "N/A",
                f"{confidence:.3f}" if confidence else "N/A"
            ])

    def get_logs(self, limit=100):
        if not os.path.exists(LOG_FILE):
            return []
        with open(LOG_FILE) as f:
            rows = list(csv.DictReader(f))
        return rows[-limit:]
