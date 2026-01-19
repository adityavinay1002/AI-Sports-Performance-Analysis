import cv2
import numpy as np
from ultralytics import YOLO
import os
import math

model = YOLO("yolov8n-pose.pt")

VIDEO_PATH = "videos/match2.mp4"
OUTPUT_PATH = "output/pose_bowling_analysis.mp4"

cap = cv2.VideoCapture(VIDEO_PATH)
os.makedirs("output", exist_ok=True)

w = int(cap.get(3))
h = int(cap.get(4))
fps = cap.get(cv2.CAP_PROP_FPS)

out = cv2.VideoWriter(
    OUTPUT_PATH,
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (w, h)
)

# store previous elbow angle per player
prev_angles = {}

def angle(a, b, c):
    """ Calculate angle at point b """
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, persist=True, conf=0.4, verbose=False)
    r = results[0]

    if r.keypoints is not None and r.boxes.id is not None:
        for i, kpts in enumerate(r.keypoints.xy):
            track_id = int(r.boxes.id[i])

            # Right arm keypoints (COCO format)
            shoulder = kpts[6]
            elbow = kpts[8]
            wrist = kpts[10]

            if 0 in shoulder or 0 in elbow or 0 in wrist:
                continue

            ang = angle(shoulder, elbow, wrist)

            if track_id in prev_angles:
                diff = abs(prev_angles[track_id] - ang)

                if diff > 15:
                    cv2.putText(
                        frame,
                        "POSSIBLE CHUCK",
                        (int(elbow[0]), int(elbow[1]) - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )

            prev_angles[track_id] = ang

            ex, ey = int(elbow[0].item()), int(elbow[1].item())
            cv2.circle(frame, (ex, ey), 5, (0, 255, 255), -1)

    annotated = r.plot()
    out.write(annotated)
    cv2.imshow("Bowling Action Analysis", annotated)

    if cv2.waitKey(30) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print("✅ Bowling action analysis saved")
