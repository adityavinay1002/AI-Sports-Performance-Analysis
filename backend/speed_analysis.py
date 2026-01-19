import cv2
import numpy as np
from ultralytics import YOLO

# Load model inside function or reuse
# heuristic: pixels to meters. 
# In a real match (cricket/football), a player is ~1.7m tall.
# We can try to estimate scale from bounding box height if we assume full body is visible.
# For simplicity in this demo, we'll use a fixed ratio or just relative units.
PIXELS_PER_METER = 50 

def analyze_speed(video_path):
    """
    Analyzes player speed in the video.
    Returns a dictionary of metrics.
    """
    model = YOLO("yolov8n.pt")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0: fps = 30
    
    # Store centroids: {track_id: [ (x,y), ... ]}
    tracks = {}
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Tracking
        results = model.track(frame, persist=True, conf=0.3, verbose=False)
        r = results[0]
        
        if r.boxes and r.boxes.id is not None:
            boxes = r.boxes.xyxy.cpu().numpy()
            track_ids = r.boxes.id.cpu().numpy()
            
            for box, track_id in zip(boxes, track_ids):
                track_id = int(track_id)
                x1, y1, x2, y2 = box
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                
                if track_id not in tracks:
                    tracks[track_id] = []
                tracks[track_id].append((cx, cy))
                
    cap.release()
    
    # Calculate speeds
    # distance = sqrt(dx^2 + dy^2)
    # speed = distance / time_interval
    # time_interval = 1/fps
    
    max_speeds = []
    avg_speeds = []
    
    # Intensity distribution (frames count)
    intensity_counts = {"Walking": 0, "Jogging": 0, "Sprinting": 0}
    total_samples = 0
    
    for tid, points in tracks.items():
        if len(points) < 2:
            continue
            
        distances = []
        for i in range(1, len(points)):
            p1 = points[i-1]
            p2 = points[i]
            dist_pixels = np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
            dist_meters = dist_pixels / PIXELS_PER_METER
            speed_mps = dist_meters * fps
            distances.append(speed_mps)
            
            # Classify
            if speed_mps < 2.0: # < 7.2 km/h
                intensity_counts["Walking"] += 1
            elif speed_mps < 5.0: # < 18 km/h
                intensity_counts["Jogging"] += 1
            else: # > 18 km/h
                intensity_counts["Sprinting"] += 1
            total_samples += 1
            
        if distances:
            avg_speeds.append(np.mean(distances))
            max_speeds.append(np.max(distances))
            
    # Aggregate metrics
    final_avg = float(np.mean(avg_speeds)) if avg_speeds else 0.0
    final_max = float(np.max(max_speeds)) if max_speeds else 0.0
    
    # Normalize percentages
    if total_samples > 0:
        intensity_dist = {
            "Walking": int((intensity_counts["Walking"] / total_samples) * 100),
            "Jogging": int((intensity_counts["Jogging"] / total_samples) * 100),
            "Sprinting": int((intensity_counts["Sprinting"] / total_samples) * 100)
        }
    else:
        intensity_dist = {"Walking": 0, "Jogging": 0, "Sprinting": 0}
        
    return {
        "average_speed": round(final_avg, 2),
        "max_speed": round(final_max, 2),
        "intensity": intensity_dist
    }
