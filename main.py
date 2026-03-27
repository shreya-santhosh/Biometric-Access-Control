"""
Biometric Access Control System
================================
Entry point. Run this file to start the application.

    python main.py

Author: Shreya Santhosh
Institution: Dr. Ambedkar Institute of Technology, Bangalore
Internship: Johnson Controls India — Security Products Division
"""

import warnings
warnings.filterwarnings("ignore")

from app_ui import App

if __name__ == "__main__":
    print("Starting Biometric Access Control System...")
    print("First enrollment downloads VGG-Face model (~500 MB) once only.")
    App().run()
