import requests
import os

class SpeechToText:
    def __init__(self, api_key, PATH):
        self.api_key = api_key
        self.base_url = "https://www.iotype.com/developer"
        self.PATH = PATH

    def transcribe_audio(self, audio_file_name):
        url = f"{self.base_url}/transcription"
        audio_file_path = os.path.join(self.PATH, "logs", f"{audio_file_name}.wav")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "multipart/form-data"
        }
        files = {'file': open(audio_file_path, 'rb')}

        try:
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response.json()  # Assuming the API returns JSON
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
