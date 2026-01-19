import cv2
import numpy as np
from ultralytics import YOLO
import os

# ---------------- CONFIG ----------------
VIDEO_PATH = r"C:\Users\adity\Downloads\AI-Based Sports Performance Analysis\videos\match.mp4"
OUTPUT_DIR = "output/player_heatmaps"
MODEL_PATH = "yolov8n.pt"

CONF_THRES = 0.3
SKIP_FRAMES = 2       # higher = faster
RADIUS = 10
BLUR = 31
# ----------------------------------------

def main():
    if not os.path.exists(VIDEO_PATH):
        print("❌ Video not found")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    model = YOLO(MODEL_PATH)

    # One heatmap per player ID
    player_heatmaps = {}

    frame_idx = 0
    last_frame = None

    print("Processing video for multi-player heatmaps using YOLOv8 tracking...")

    # Use model.track on the video source so tracker maintains IDs across frames
    try:
        results_iter = model.track(source=VIDEO_PATH, persist=True, conf=CONF_THRES, classes=[0], show=False)
    except TypeError:
        # Older/newer API differences: try without named args
        results_iter = model.track(VIDEO_PATH, persist=True, conf=CONF_THRES, classes=[0], show=False)

    for res in results_iter:
        # Get the frame image from result if available
        frame = getattr(res, 'orig_img', None)
        if frame is None:
            # fallback: skip if no frame
            continue

        last_frame = frame.copy()
        h, w = frame.shape[:2]

        if frame_idx % SKIP_FRAMES != 0:
            frame_idx += 1
            continue

        boxes_obj = getattr(res, 'boxes', None)
        if boxes_obj is None:
            frame_idx += 1
            continue

        xyxy = getattr(boxes_obj, 'xyxy', None)
        ids = getattr(boxes_obj, 'id', None)
        confs = getattr(boxes_obj, 'conf', None)

        if xyxy is None:
            frame_idx += 1
            continue

        xy = np.array(xyxy.cpu()) if hasattr(xyxy, 'cpu') else np.array(xyxy)
        ids_arr = None
        confs_arr = None
        if ids is not None:
            ids_arr = np.array(ids.cpu()) if hasattr(ids, 'cpu') else np.array(ids)
        if confs is not None:
            confs_arr = np.array(confs.cpu()) if hasattr(confs, 'cpu') else np.array(confs)

        for i, box in enumerate(xy):
            conf = float(confs_arr[i]) if confs_arr is not None else 1.0
            if conf < CONF_THRES:
                continue

            tid = int(ids_arr[i]) if (ids_arr is not None) else None
            if tid is None:
                # No track id available — skip
                continue

            x1, y1, x2, y2 = box.astype(int)
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            if tid not in player_heatmaps:
                player_heatmaps[tid] = np.zeros((h, w), dtype=np.float32)

            if 0 <= cx < w and 0 <= cy < h:
                cv2.circle(player_heatmaps[tid], (cx, cy), RADIUS, 255, -1)

        frame_idx += 1

    # Save per-player heatmaps overlaid on last_frame
    if last_frame is None:
        print('No frames processed, nothing to save.')
        return

    for pid, heatmap in player_heatmaps.items():
        heatmap = cv2.GaussianBlur(heatmap, (BLUR | 1, BLUR | 1), 0)
        heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap = heatmap.astype(np.uint8)

        colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(last_frame, 0.6, colored, 0.4, 0)

        out_path = os.path.join(OUTPUT_DIR, f"player_{pid}_heatmap.png")
        cv2.imwrite(out_path, overlay)

        print(f"✅ Saved heatmap for Player ID {pid} -> {out_path}")

    print("🎉 All player heatmaps generated successfully!")


if __name__ == "__main__":
    main()
