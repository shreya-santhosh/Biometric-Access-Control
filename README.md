# Biometric Access Control System

Multi-modal biometric authentication combining facial recognition and height 
verification for role-based physical access control. Extended from internship 
work at Johnson Controls India — Security Products Division.

## What It Does

Two-factor biometric authentication where both factors must independently verify 
before access is granted:
- **Factor 1** — Facial recognition using DeepFace VGG-Face embeddings
- **Factor 2** — Height verification via OpenCV body detection (±8cm tolerance)

An attacker who spoofs a face cannot gain access without simultaneously matching 
the registered height profile — defeating photo and screen spoofing attacks.

## Access Roles

| Decision | Condition |
|----------|-----------|
| ADMIN | Face matched + height matched + role = ADMIN |
| EMPLOYEE | Face matched + height matched + role = EMPLOYEE |
| VISITOR | Face detected but not enrolled |
| DENIED | Face matched but height mismatch — spoofing attempt flagged |

## Security Architecture
```
Camera → Distance Estimation (Single View Metrology)
       → Face Recognition (DeepFace VGG-Face)
       → Height Verification (OpenCV)
       → Access Decision Engine
       → Role-Based Access (ADMIN / EMPLOYEE / VISITOR / DENIED)
       → Tamper-Evident Access Log
```

## Anti-Spoofing

Height mismatch detection catches 2D spoofing attacks. If someone holds a photo 
of an enrolled user, their measured height will not match the registered profile 
and access is denied with an alert logged.

## Threat Model (STRIDE)

| Threat | Attack | Mitigation |
|--------|--------|-----------|
| Spoofing | Photo of enrolled user | Height mismatch detection |
| Tampering | Modify user database | Server-side role storage |
| Repudiation | Deny access attempt | Timestamped access log |
| Info Disclosure | Extract face encodings | Stored as embeddings not images |
| Elevation of Privilege | Claim admin role | Role verified server-side |

## Tech Stack

Python, DeepFace, OpenCV, Tkinter, JSON, CSV

## Project Structure
```
main.py           — Entry point
config.py         — All constants and thresholds  
engine.py         — Biometric processing pipeline
database.py       — User records and access logging
app_ui.py         — Main application UI
enroll_window.py  — User enrollment interface
logs_window.py    — Access log viewer
```

## Installation
```bash
pip install deepface opencv-python Pillow tensorflow
python main.py
```

## Background

Extended from internship work at Johnson Controls India Pvt. Ltd. (Aug–Sep 2024) 
under the Associate Engineering Director of Security Products, Bangalore. 
Original system used facial detection and height estimation for employee 
authentication. This version adds full facial recognition, role-based access 
control, anti-spoofing via biometric cross-validation, and tamper-evident logging.

**Author:** Shreya Santhosh  
**Institution:** Dr. Ambedkar Institute of Technology, Bangalore  
**Contact:** shreyasanthosh2004@gmail.com
