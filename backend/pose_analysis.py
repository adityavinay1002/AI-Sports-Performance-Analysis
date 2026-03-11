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
    # Adding timestamp to ensure unique filename for browser cache busting
    import time
    timestamp = int(time.time())
    output_filename = f"pose_{clean_base}_{timestamp}.webm"
    output_path = os.path.join(output_dir, output_filename)
    
    cap = cv2.VideoCapture(video_path)
    
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Skip frames control
    skip_frames = 2 # Process every 3rd frame
    adjusted_fps = fps / (skip_frames + 1)

    # Try vp80 first, fallback to mp4v
    fourcc = cv2.VideoWriter_fourcc(*"vp80")
    out = cv2.VideoWriter(output_path, fourcc, adjusted_fps, (w, h))
    
    if not out.isOpened():
        print("Warning: vp80 codec failed in analyze_pose, falling back to mp4v")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, adjusted_fps, (w, h))

    if not out.isOpened():
        print(f"Error: Could not initialize VideoWriter for {output_path}")
        cap.release()
        return None, {}
    
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
    
    frame_count = 0
    # skip_frames moved up to VideoWriter initialization
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        if frame_count % (skip_frames + 1) != 0:
            continue
            
        if frame_count % 30 == 0:
            print(f"Pose analysis processing frame {frame_count}...")
            
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
                            
                            # Removed "POSSIBLE CHUCK" logic as requested
                            
                            prev_angles[track_id] = ang
                            
                            ex, ey = int(elbow[0]), int(elbow[1])
                            cv2.circle(frame, (ex, ey), 5, (0, 255, 255), -1)

        annotated = r.plot()
        out.write(annotated)
        
    cap.release()
    out.release()
    
    avg_elbow_angle = np.mean(list(prev_angles.values())) if prev_angles else 0.0
    
    return output_path, {"elbow_angle": round(float(avg_elbow_angle), 2)}

def torch_is_zero(t):
    # tensor check helper if inputs are tensors
    if hasattr(t, 'sum'):
        return t.sum() == 0
    # numpy / list check
    return np.sum(t) == 0
