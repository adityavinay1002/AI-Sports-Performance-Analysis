import cv2
import numpy as np
import os

def generate_heatmap(video_path):
    cap = cv2.VideoCapture(video_path)
    heatmap = None
    
    # Determine output path relative to this file or CWD
    # Ideally should use the same logical directory as main.py
    # Assuming CWD is 'backend/' or we use absolute paths if provided.
    # But main.py calls it.
    
    # Better approach: Saves to 'outputs' directory in CWD
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "heatmap.png")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        if heatmap is None:
            heatmap = np.zeros((h, w), dtype=np.float32)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        heatmap += gray / 255.0

    if heatmap is not None:
        heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap = heatmap.astype(np.uint8)
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        cv2.imwrite(output_path, heatmap)

    cap.release()
    # return simple filename or path relative to CWD?
    # main.py expects to return URL.
    # main.py expects a path to identify the file.
    return output_path
