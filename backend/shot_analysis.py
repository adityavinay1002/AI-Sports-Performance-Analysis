import cv2
import numpy as np
import os
from ultralytics import YOLO
from angle_utils import calculate_angle, calculate_distance
from shot_classifier import classify_shot

# Initialize model
model = YOLO("yolov8n-pose.pt")

def analyze_cricket_shot(video_path, output_dir):
    """
    Analyzes a cricket batting video, detects shots, and overlays analytics.
    Returns the path to the processed output video.
    """
    
    # Generate output filename
    import re
    filename = os.path.basename(video_path)
    name_only = os.path.splitext(filename)[0]
    # Replace non-alphanumeric characters with _ to be URL safe
    clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', name_only)
    
    # Adding timestamp to ensure unique filename for browser cache busting
    import time
    timestamp = int(time.time())
    output_path = os.path.join(output_dir, f"shot_analysis_{clean_name}_{timestamp}.mp4")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")
        
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Initialize writer
    # Try avc1 first (H.264), fallback to mp4v
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        print(f"Warning: avc1 codec failed, falling back to mp4v")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        cap.release()
        raise ValueError("Could not open VideoWriter with avc1 or mp4v")
    
    shot_name = "Rest Shot"
    frame_count = 0
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Run YOLO inference
            results = model(frame, verbose=False)
            
            for r in results:
                # Visualize the skeletal keypoints
                annotated_frame = r.plot()
                frame = annotated_frame 

                if r.keypoints and r.keypoints.data.shape[1] >= 17:
                    kpts = r.keypoints.data[0].cpu().numpy()
                    
                    # Helper to get (x,y)
                    def get_pt(idx):
                        return kpts[idx][:2]
                    
                    nose = get_pt(0)
                    left_shoulder = get_pt(5)
                    right_shoulder = get_pt(6)
                    left_elbow = get_pt(7)
                    right_elbow = get_pt(8)
                    left_wrist = get_pt(9)
                    right_wrist = get_pt(10)
                    left_hip = get_pt(11)
                    right_hip = get_pt(12)
                    left_knee = get_pt(13)
                    right_knee = get_pt(14)
                    left_ankle = get_pt(15)
                    right_ankle = get_pt(16)
                    
                    right_elbow_ang = calculate_angle(right_shoulder, right_elbow, right_wrist)
                    left_elbow_ang = calculate_angle(left_shoulder, left_elbow, left_wrist)
                    
                    right_hip_ang = calculate_angle(right_shoulder, right_hip, right_knee)
                    left_hip_ang = calculate_angle(left_shoulder, left_hip, left_knee)
                    
                    right_knee_ang = calculate_angle(right_hip, right_knee, right_ankle)
                    left_knee_ang = calculate_angle(left_hip, left_knee, left_ankle)
                    
                    def normalize(pt):
                         return [pt[0] / width, pt[1] / height]
                    
                    wrist_nose_dist = calculate_distance(normalize(right_wrist), normalize(nose)) * 100
                    right_left_leg_dist = calculate_distance(normalize(right_ankle), normalize(left_ankle)) * 100
                    
                    angles_map = {
                        'right_knee': right_knee_ang,
                        'left_knee': left_knee_ang,
                        'right_elbow': right_elbow_ang,
                        'left_elbow': left_elbow_ang,
                        'right_hip': right_hip_ang,
                        'left_hip': left_hip_ang
                    }
                    
                    dist_map = {
                        'wrist_nose': wrist_nose_dist,
                        'right_left_leg': right_left_leg_dist
                    }
                    
                    # Classify Shot
                    detected_shot = classify_shot(angles_map, dist_map)
                    if detected_shot != "Rest Shot":
                        shot_name = detected_shot
                    
                    # Draw Analytics
                    cv2.putText(frame, f"SHOT: {shot_name}", (30, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 10), 5)
                    cv2.putText(frame, f"SHOT: {shot_name}", (30, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.32, (0, 0, 0), 2)
                               
                    y_pos = 150
                    gap = 50
                    
                    def draw_text(txt, y, color=(0, 0, 255)):
                        cv2.putText(frame, txt, (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.71, color, 2)
                        cv2.putText(frame, txt, (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)

                    draw_text(f"R Knee: {int(right_knee_ang)}", y_pos)
                    draw_text(f"R Elbow: {int(right_elbow_ang)}", y_pos + gap)
                    draw_text(f"L Elbow: {int(left_elbow_ang)}", y_pos + 2*gap)
                    draw_text(f"L Knee: {int(left_knee_ang)}", y_pos + 3*gap)
                    draw_text(f"R Hip: {int(right_hip_ang)}", y_pos + 4*gap)
                    draw_text(f"L Hip: {int(left_hip_ang)}", y_pos + 5*gap)

            out.write(frame)
            
    except Exception as e:
        print(f"Error during video processing: {e}")
        raise
        
    finally:
        cap.release()
        out.release()
    
    # Verify file creation
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Output video was not created at {output_path}")
        
    file_size = os.path.getsize(output_path)
    if file_size == 0:
        raise ValueError(f"Output video size is 0 bytes at {output_path}")
        
    print(f"Video saved successfully: {output_path} (Size: {file_size/1024/1024:.2f} MB)")
    return output_path
