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
```

Scroll down and click **Commit changes**.

---

**Step 2 — Add repository description**

On your repository page click the gear icon next to About on the right side. Add this description:
```
Multi-modal biometric access control combining DeepFace facial recognition and height verification for RBAC. Built on Johnson Controls Security Products internship work.
```

Add these topics one by one:
```
biometric-security
access-control
deepface
opencv
python
cybersecurity
computer-vision
rbac
```

Click Save changes.

---

**Step 3 — Add requirements.txt**

Click Add file → Create new file. Name it `requirements.txt`. Paste:
```
deepface>=0.0.79
opencv-python>=4.8.0
Pillow>=10.0.0
tensorflow>=2.13.0
numpy>=1.24.0
```

Commit the file.

---

**Step 4 — Pin this repository on your profile**

Go to github.com/shreya-santhosh. Click Customize your profile or the pin repositories option. Pin both Malware-Detection-ML and Biometric-Access-Control so they appear first on your profile. Anyone who opens your GitHub tomorrow will see both projects immediately.

---

**Step 5 — Bookmark these two URLs on your phone right now**
```
github.com/shreya-santhosh/Biometric-Access-Control
github.com/shreya-santhosh/Malware-Detection-ML
