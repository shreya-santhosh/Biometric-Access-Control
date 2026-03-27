"""
Configuration and constants for the Biometric Access Control System.
All tunable parameters live here — change this file to adjust system behaviour.
"""

# ── Camera & Distance ─────────────────────────────────────────────────────────
KNOWN_DISTANCE_CM   = 60.96   # Calibration distance in cm
KNOWN_FACE_WIDTH_CM = 14.3    # Average human face width in cm
OPTIMAL_DIST_MIN    = 90      # Minimum distance for valid measurement (cm)
OPTIMAL_DIST_MAX    = 130     # Maximum distance for valid measurement (cm)

# ── Biometric Thresholds ──────────────────────────────────────────────────────
HEIGHT_TOLERANCE_CM = 8       # Allowed deviation from registered height (cm)
COSINE_THRESHOLD    = 0.40    # Face recognition strictness (lower = stricter)

# ── File Paths ────────────────────────────────────────────────────────────────
ENROLLED_FACES_DIR = "enrolled_faces"
DATABASE_FILE      = "database/users.json"
LOG_FILE           = "logs/access_log.csv"
EMBEDDINGS_FILE    = "database/embeddings.json"

# ── DeepFace Settings ─────────────────────────────────────────────────────────
DEEPFACE_MODEL    = "VGG-Face"
DEEPFACE_BACKEND  = "opencv"

# ── UI Colour Palette ─────────────────────────────────────────────────────────
BG_DARK      = "#0a0f1e"
BG_CARD      = "#111827"
BG_PANEL     = "#1a2235"
ACCENT_BLUE  = "#2563eb"
ACCENT_GREEN = "#10b981"
ACCENT_RED   = "#ef4444"
ACCENT_AMBER = "#f59e0b"
TEXT_PRI     = "#f1f5f9"
TEXT_SEC     = "#94a3b8"
