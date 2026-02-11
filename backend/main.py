from fastapi import FastAPI, UploadFile, File, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import cv2
import numpy as np
from ultralytics import YOLO

# Import local modules
from pose_analysis import analyze_pose
from heatmap import generate_heatmap
from speed_analysis import analyze_speed
from shot_analysis import analyze_cricket_shot

# ------------------ APP SETUP ------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Serve output files (videos & images)
app.mount("/backend/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# Load YOLO model
model = YOLO("yolov8n.pt")

# ------------------ MODELS ------------------

class ProcessRequest(BaseModel):
    filename: str
    analyses: List[str]  # e.g. ["tracking", "heatmap", "pose", "speed", "shot_analysis"]

# ------------------ ENDPOINTS ------------------

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@app.post("/process")
def process_video(req: ProcessRequest):
    input_path = os.path.join(UPLOAD_DIR, req.filename)
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="File not found")

    outputs = []
    
    # Helper to clean filenames
    def clean_filename(fname):
        import re
        # Keep dots for extension, replace others
        name, ext = os.path.splitext(fname)
        clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', name) # Replace non-alphanum with _
        return f"{clean_name}{ext}"

    # 1. TRACKING
    if "tracking" in req.analyses:
        print(f"Starting tracking for {req.filename}...")
        safe_name = clean_filename(f"tracked_{req.filename}")
        tracked_path = os.path.join(OUTPUT_DIR, safe_name)
        process_tracking(input_path, tracked_path)
        print(f"Tracking completed: {tracked_path}")
        outputs.append({
            "name": "Player Tracking",
            "url": f"/backend/outputs/{safe_name}"
        })

    # 2. HEATMAP
    if "heatmap" in req.analyses:
        print(f"Starting heatmap for {req.filename}...")
        try:
            out_abs_path = generate_heatmap(input_path)
            out_filename = os.path.basename(out_abs_path)
            outputs.append({
                "name": "Heatmap",
                "url": f"/backend/outputs/{out_filename}"
            })
            print(f"Heatmap completed: {out_filename}")
        except Exception as e:
            print(f"Heatmap error: {e}")

    # 3. POSE
    if "pose" in req.analyses:
        print(f"Starting pose analysis for {req.filename}...")
        try:
            out_abs_path = analyze_pose(input_path, OUTPUT_DIR)
            out_filename = os.path.basename(out_abs_path)
            outputs.append({
                "name": "Pose Analysis",
                "url": f"/backend/outputs/{out_filename}"
            })
            print(f"Pose analysis completed: {out_filename}")
        except Exception as e:
            print(f"Pose error: {e}")
            
    # 4. SPEED
    if "speed" in req.analyses:
        print(f"Starting speed analysis for {req.filename}...")
        try:
            metrics = analyze_speed(input_path)
            outputs.append({
                "name": "Player Speed Analysis",
                "type": "speed_analysis",
                "data": metrics,
                "url": "#" 
            })
            print(f"Speed analysis completed.")
        except Exception as e:
            print(f"Speed error: {e}")
            with open("speed_error.log", "w") as f:
                f.write(str(e))
                import traceback
                traceback.print_exc(file=f)

    # 5. SHOT ANALYSIS
    if "shot_analysis" in req.analyses:
        print(f"Starting cricket shot analysis for {req.filename}...")
        try:
            out_abs_path = analyze_cricket_shot(input_path, OUTPUT_DIR)
            out_filename = os.path.basename(out_abs_path)
            outputs.append({
                "name": "Cricket Shot Analysis",
                "url": f"/backend/outputs/{out_filename}"
            })
            print(f"Shot analysis completed: {out_filename}")
        except Exception as e:
            print(f"Shot analysis error: {e}")
            import traceback
            traceback.print_exc()
            
    return {"outputs": outputs}

def process_tracking(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error opening video file: {input_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video info: {width}x{height} @ {fps}fps, {total_frames} frames")
    
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"avc1"), fps, (width, height))
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % 10 == 0:
            print(f"Processing frame {frame_count}/{total_frames} ({frame_count/total_frames*100:.1f}%)")
            
        results = model(frame, conf=0.4, verbose=False)
        for r in results:
            if r.boxes:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    if cls == 0: # person
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        out.write(frame)
    
    print("Tracking processing finished.")
    cap.release()
    out.release()

@app.post("/analyze")
async def analyze(video: UploadFile = File(...)):
    # Save uploaded video
    input_path = os.path.join(UPLOAD_DIR, video.filename)
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    # Run everything
    tracked_path = os.path.join(OUTPUT_DIR, "tracked.mp4")
    process_tracking(input_path, tracked_path)
    
    # Heatmap
    heatmap_path = generate_heatmap(input_path)
    
    return {
        "tracked_video": "/backend/outputs/tracked.mp4",
        "heatmap": f"/backend/outputs/{os.path.basename(heatmap_path)}"
    }
