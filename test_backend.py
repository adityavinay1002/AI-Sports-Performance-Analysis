import requests
import os

API_URL = "http://localhost:8000"
VIDEO_PATH = "videos/match2.mp4" # Assuming this exists from file list in root, but user has it in root.
# Actually file list showed 'videos' in root. `pose.py` referenced `videos/match2.mp4`.
# Let's check if we can access it.

def test_api():
    # 1. Upload
    print("Testing /upload...")
    if not os.path.exists(VIDEO_PATH):
        # try referencing relative to root if script is run from root
        # or just create a dummy file
        with open("test_video.mp4", "wb") as f:
            f.write(b"dummy content")
        video_file = "test_video.mp4"
    else:
        video_file = VIDEO_PATH

    try:
        with open(video_file, "rb") as f:
            files = {"file": f}
            resp = requests.post(f"{API_URL}/upload", files=files)
        
        if resp.status_code != 200:
            print(f"Upload failed: {resp.text}")
            return
            
        print(f"Upload success: {resp.json()}")
        filename = resp.json()["filename"]
        
        # 2. Process
        print("Testing /process...")
        payload = {
            "filename": filename,
            "analyses": ["tracking", "heatmap"] # skipping pose for speed/dummy check, or include it if confident
        }
        
        # If dummy content, CV2 might fail.
        # So unless we have a real video, we might get 500 from CV2.
        # But at least we reach the endpoint.
        
        resp = requests.post(f"{API_URL}/process", json=payload)
        # We expect 200 or 500 (if video is invalid)
        print(f"Process status: {resp.status_code}")
        print(f"Process response: {resp.text}")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_api()
