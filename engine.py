"""
Biometric processing engine.
Handles distance estimation, face recognition, height measurement,
and access decision logic.
Uses OpenCV only — no mediapipe dependency.
"""

import cv2
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from config import (
    KNOWN_DISTANCE_CM, KNOWN_FACE_WIDTH_CM,
    HEIGHT_TOLERANCE_CM, COSINE_THRESHOLD,
    DEEPFACE_MODEL, DEEPFACE_BACKEND
)

_deepface = None

def get_deepface():
    global _deepface
    if _deepface is None:
        from deepface import DeepFace
        _deepface = DeepFace
    return _deepface


class BiometricEngine:
    def __init__(self, db):
        self.db = db
        self.focal_length = None

        self.face_det = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.body_det = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_fullbody.xml"
        )

    def calibrate(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_det.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            w = faces[0][2]
            self.focal_length = (w * KNOWN_DISTANCE_CM) / KNOWN_FACE_WIDTH_CM
            return True
        return False

    def distance(self, frame):
        if self.focal_length is None:
            return None, None
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_det.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0:
            return None, None
        x, y, w, h = faces[0]
        return (KNOWN_FACE_WIDTH_CM * self.focal_length) / w, (x, y, w, h)

    def recognize(self, frame):
        try:
            DeepFace = get_deepface()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = DeepFace.represent(
                img_path=rgb,
                model_name=DEEPFACE_MODEL,
                enforce_detection=False,
                detector_backend=DEEPFACE_BACKEND
            )
            if not result:
                return "UNKNOWN", 0.0, None

            query_emb = np.array(result[0]["embedding"])
            fa = result[0].get("facial_area")
            box = (fa["x"], fa["y"], fa["w"], fa["h"]) if fa else None

            if not self.db.embeddings:
                return "UNKNOWN", 0.0, box

            best_uid, best_sim = None, -1.0
            for uid, stored_emb in self.db.embeddings.items():
                stored = np.array(stored_emb)
                sim = float(
                    np.dot(query_emb, stored) /
                    (np.linalg.norm(query_emb) * np.linalg.norm(stored) + 1e-10)
                )
                if sim > best_sim:
                    best_sim, best_uid = sim, uid

            if best_sim >= (1.0 - COSINE_THRESHOLD):
                return best_uid, best_sim, box
            return "UNKNOWN", best_sim, box

        except Exception:
            return None, 0.0, None

    def enroll_face(self, frame, user_id):
        try:
            DeepFace = get_deepface()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = DeepFace.represent(
                img_path=rgb,
                model_name=DEEPFACE_MODEL,
                enforce_detection=False,
                detector_backend="skip"
            )
            if result:
                self.db.save_embedding(user_id, result[0]["embedding"])
                return True
        except Exception as e:
            print(f"Enrollment error: {e}")
        return False

    def height(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bodies = self.body_det.detectMultiScale(
            gray, 1.1, 3, minSize=(50, 100)
        )
        annotated = frame.copy()
        h_cm = None

        if len(bodies) > 0:
            x, y, w, h = bodies[0]
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 100), 2)
            h_cm = (h / frame.shape[0]) * 215
            cv2.putText(
                annotated,
                f"{h_cm:.1f} cm",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 100),
                2
            )

        return h_cm, annotated

    def decide(self, user_id, measured_height):
        if user_id is None or user_id == "UNKNOWN":
            return "VISITOR", None
        user = self.db.get_user(user_id)
        if not user:
            return "DENIED", None
        if measured_height is None:
            return "DENIED", user
        height_ok = abs(measured_height - user["height_cm"]) <= HEIGHT_TOLERANCE_CM
        return (user["role"], user) if height_ok else ("DENIED", user)
