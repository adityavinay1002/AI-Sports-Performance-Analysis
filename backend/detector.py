from ultralytics import YOLO
import cv2
import os

model = YOLO("yolov8n.pt")

def detect_players(video_path):
    cap = cv2.VideoCapture(video_path)

    out_path = "backend/outputs/tracked.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, 30,
                          (int(cap.get(3)), int(cap.get(4))))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=0.4)
        annotated = results[0].plot()
        out.write(annotated)

    cap.release()
    out.release()

    return out_path
