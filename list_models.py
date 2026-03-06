import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv('GEMINI_API_KEY')
url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'

try:
    response = requests.get(url)
    models = response.json().get('models', [])
    with open('models.txt', 'w') as f:
        for m in models:
            f.write(f"{m['name']}\n")
    print(f"Wrote {len(models)} models to models.txt")
except Exception as e:
    print(f"Error: {e}")
