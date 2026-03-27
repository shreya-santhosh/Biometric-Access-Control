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
