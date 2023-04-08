import os
import requests
from dotenv import load_dotenv

# Load API key from the .env file
load_dotenv()
api_key = str(os.getenv('ELEVEN_LABS_API_KEY'))

# Define the API endpoint and headers
url = "https://api.elevenlabs.io/v1/voices"
headers = {"xi-api-key": api_key}

# Make the GET request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    voices = data["voices"]

    # Print voice names and voice IDs
    for voice in voices:
        print(f"Name: {voice['name']}, Voice ID: {voice['voice_id']}")
else:
    print(f"Error: {response.status_code}, {response.text}")
