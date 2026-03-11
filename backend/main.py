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

# Import local modules (use package-relative paths since backend is a package)
from .pose_analysis import analyze_pose
from .heatmap import generate_heatmap
from .speed_analysis import analyze_speed
from .shot_analysis import analyze_cricket_shot
from .ai_coach import get_coaching_feedback
from .voice_utils import transcribe_audio

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

class CoachingRequest(BaseModel):
    question: str
    metrics: dict

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
    aggregated_metrics = {}
    
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
            out_abs_path, metrics = analyze_pose(input_path, OUTPUT_DIR)
            out_filename = os.path.basename(out_abs_path)
            outputs.append({
                "name": "Pose Analysis",
                "url": f"/backend/outputs/{out_filename}"
            })
            aggregated_metrics.update(metrics)
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
            aggregated_metrics.update(metrics)
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
            out_abs_path, metrics = analyze_cricket_shot(input_path, OUTPUT_DIR)
            out_filename = os.path.basename(out_abs_path)
            outputs.append({
                "name": "Cricket Shot Analysis",
                "url": f"/backend/outputs/{out_filename}"
            })
            aggregated_metrics.update(metrics)
            print(f"Shot analysis completed: {out_filename}")
        except Exception as e:
            print(f"Shot analysis error: {e}")
            import traceback
            traceback.print_exc()
            
    return {"outputs": outputs, "aggregated_metrics": aggregated_metrics}

def process_tracking(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error opening video file: {input_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    frame_count = 0
    skip_frames = 2 # Process every 3rd frame
    
    # Adjust FPS for frame skipping so playback speed is correct
    adjusted_fps = fps / (skip_frames + 1)
    
    # Try avc1 first, fallback to mp4v
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    out = cv2.VideoWriter(output_path, fourcc, adjusted_fps, (width, height))
    
    if not out.isOpened():
        print("Warning: avc1 codec failed in process_tracking, falling back to mp4v")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, adjusted_fps, (width, height))

    if not out.isOpened():
        print(f"Error: Could not initialize VideoWriter with avc1 or mp4v for {output_path}")
        cap.release()
        return
    
    frame_count = 0
    skip_frames = 2 # Process every 3rd frame
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % (skip_frames + 1) != 0:
            continue

        if frame_count % 30 == 0:
            print(f"Tracking processing frame {frame_count}/{total_frames} ({frame_count/total_frames*100:.1f}%)")
            
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

@app.post("/ai-coach")
async def ai_coach(req: CoachingRequest):
    try:
        feedback = get_coaching_feedback(req.metrics, req.question)
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    temp_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = transcribe_audio(temp_path)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
