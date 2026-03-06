import sys
import os

# Add the current directory to path to allow absolute imports of 'backend'
sys.path.append(os.getcwd())

print("Attempting to import backend.main...")
try:
    import backend.main
    print("Successfully imported backend.main")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
