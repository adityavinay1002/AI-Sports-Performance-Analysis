import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY not found in environment variables.")

def get_coaching_feedback(metrics: dict, question: str) -> str:
    """
    Generates coaching feedback using Gemini LLM REST API based on player metrics.
    """
    if not api_key:
        return "AI Coach is currently unavailable. Please check the API key configuration."

    try:
        # Define the prompt
        prompt = f"""
You are a professional cricket coach. 
Analyze the following player performance metrics and answer the coach's question.
Provide clear, actionable coaching feedback explaining where the player can improve.

Player performance metrics:
- Speed: {metrics.get('speed', 'N/A')} m/s
- Average Speed: {metrics.get('average_speed', 'N/A')} m/s
- Max Speed: {metrics.get('max_speed', 'N/A')} m/s
- Elbow Angle: {metrics.get('elbow_angle', 'N/A')} degrees
- Swing Angle: {metrics.get('swing_angle', 'N/A')} degrees
- Balance: {metrics.get('balance', 'N/A')}
- Shot Type: {metrics.get('shot_type', 'N/A')}
- Intensity: {metrics.get('intensity', 'N/A')}

Coach question: {question}

Response format:
Provide a concise but insightful response. Use bullet points if necessary.
"""

        # Gemini REST API URL (using gemini-flash-latest)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        if response.status_code == 200:
            return response_data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            error_msg = response_data.get('error', {}).get('message', 'Unknown error')
            print(f"Gemini API Error: {error_msg}")
            return f"Sorry, I encountered an error from the AI service: {error_msg}"

    except Exception as e:
        print(f"Error generating coaching feedback: {e}")
        return f"Sorry, I encountered an error while generating feedback: {str(e)}"

# Example usage for testing
if __name__ == "__main__":
    test_metrics = {
        "speed": 7.2,
        "elbow_angle": 145,
        "shot_type": "Straight Drive",
        "balance": "Excellent"
    }
    test_question = "What should the player improve in this shot?"
    print(get_coaching_feedback(test_metrics, test_question))
