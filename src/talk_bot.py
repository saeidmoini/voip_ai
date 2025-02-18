import requests
import json
from src.logger_config import logger, PATH
import asyncio


class TalkBot:
    def __init__(self, access_token):
        self.api_url = 'https://api.talkbot.ir/v1/media/speech-to-text/REQ'
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    async def speech_to_text(self, url, language='fa'):
        data = {
            'url': url,
            'language': language
        }

        response = requests.post(self.api_url, json=data, headers=self.headers)
        return response.json()