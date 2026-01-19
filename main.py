# main.py
from ultralytics import YOLO
import os

# ---------------- PATHS ----------------
video_path = "videos/match.mp4"
os.makedirs("output", exist_ok=True)

# ---------------- LOAD MODEL ----------------
model = YOLO("yolov8n.pt")

# ---------------- TRACK ----------------
results = model.track(
    source=video_path,
    tracker="bytetrack.yaml",  # built-in tracker
    persist=True,
    save=True,
    show=True,
    classes=[0]  # only detect people
)

print("✅ Tracking complete!")
print("📁 Output saved inside: runs/track/")
