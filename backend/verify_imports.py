import sys
import os
sys.path.append(os.getcwd())

try:
    print("Importing angle_utils...")
    import angle_utils
    print("angle_utils imported successfully.")
    
    print("Importing shot_classifier...")
    import shot_classifier
    print("shot_classifier imported successfully.")
    
    print("Importing shot_analysis...")
    import shot_analysis
    print("shot_analysis imported successfully.")
    
    print("Importing main...")
    import main
    print("main imported successfully.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
