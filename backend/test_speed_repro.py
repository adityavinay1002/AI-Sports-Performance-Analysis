import sys
import os

# Add backend dir to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from speed_analysis import analyze_speed

video_path = "c:\\Users\\adity\\Downloads\\AI-Based Sports Performance Analysis\\backend\\uploads\\Mitchell_Starc_vs_Shaheen_Afridi_shorts_cricket_viral_360P.mp4"

try:
    print(f"Testing speed analysis on {video_path}...")
    result = analyze_speed(video_path)
    print("Success!")
    print(result)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
