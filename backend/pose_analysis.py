import cv2
import numpy as np
from ultralytics import YOLO
import os

# Load model once if possible, or inside function to avoid global state issues if reloaded
# For now, loading at module level is fine for this simple app
model = YOLO("yolov8n-pose.pt")

def analyze_pose(video_path, output_dir):
    """
    Analyzes the video for bowling action correctness.
    Returns the path to the annotated output video.
    """
    
    # Ensure output filename is unique or specific
    import re
    filename = os.path.basename(video_path)
    base, ext = os.path.splitext(filename)
    # Sanitize base name
    clean_base = re.sub(r'[^a-zA-Z0-9_\-]', '_', base)
    output_filename = f"pose_{clean_base}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    cap = cv2.VideoCapture(video_path)
    
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"avc1"),
        fps,
        (w, h)
    )
    
    # store previous elbow angle per player
    prev_angles = {}
    
    def calculate_angle(a, b, c):
        """ Calculate angle at point b """
        ba = np.array(a) - np.array(b)
        bc = np.array(c) - np.array(b)
        
        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)
        
        if norm_ba == 0 or norm_bc == 0:
            return 0.0
            
        cos_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        results = model.track(frame, persist=True, conf=0.4, verbose=False)
        if not results:
             out.write(frame)
             continue
             
        r = results[0]
        
        if r.keypoints is not None and r.boxes.id is not None:
            # Check if we have valid keypoints data
            if hasattr(r.keypoints, 'xy') and len(r.keypoints.xy) > 0:
                for i, kpts in enumerate(r.keypoints.xy):
                    if i >= len(r.boxes.id):
                        break
                        
                    track_id = int(r.boxes.id[i])
                    
                    # Ensure we have enough keypoints (COCO has 17)
                    if len(kpts) > 10:
                        # Right arm keypoints (COCO format): shoulder 6, elbow 8, wrist 10
                        shoulder = kpts[6]
                        elbow = kpts[8]
                        wrist = kpts[10]
                        
                        # Check confidence or if points are zero (sometimes simpler models return 0)
                        if not (torch_is_zero(shoulder) or torch_is_zero(elbow) or torch_is_zero(wrist)):
                            ang = calculate_angle(shoulder.cpu().numpy(), elbow.cpu().numpy(), wrist.cpu().numpy())
                            
                            if track_id in prev_angles:
                                diff = abs(prev_angles[track_id] - ang)
                                
                                # Threshold for "chucking" detection (simple heuristic)
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
                            
                            ex, ey = int(elbow[0]), int(elbow[1])
                            cv2.circle(frame, (ex, ey), 5, (0, 255, 255), -1)

        annotated = r.plot()
        out.write(annotated)
        
    cap.release()
    out.release()
    
    return output_path

def torch_is_zero(t):
    # tensor check helper if inputs are tensors
    if hasattr(t, 'sum'):
        return t.sum() == 0
    # numpy / list check
    return np.sum(t) == 0
