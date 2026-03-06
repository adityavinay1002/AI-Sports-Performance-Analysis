import requests

API_URL = "http://localhost:8000"

def test_ai_coach():
    print("Testing /ai-coach...")
    payload = {
        "question": "What should the player improve in this shot?",
        "metrics": {
            "speed": 7.2,
            "elbow_angle": 145,
            "shot_type": "Straight Drive",
            "balance": "Excellent"
        }
    }
    
    try:
        resp = requests.post(f"{API_URL}/ai-coach", json=payload)
        if resp.status_code == 200:
            print("AI Coach Feedback:")
            print(resp.json()["feedback"])
        else:
            print(f"Error: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_ai_coach()
