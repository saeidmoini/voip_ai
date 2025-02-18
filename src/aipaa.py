from src.logger_config import logger, PATH
import asyncio
import os
import json
import requests
from pydub import AudioSegment

class Aipaa:
    TTS_URL = "https://api.aipaa.ir/api/v1/voice/tts/?expire-file=yes"
    DOWNLOAD_URL = "https://api.aipaa.ir/api/v1/file_manager/file/download/{id}/"
    TOKEN_URL = "https://api.aipaa.ir/auth/token/"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = self.authenticate()
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def authenticate(self):

        payload = {
            'username': self.username,
            'password': self.password,
            'client_id': 'cK5uzw5ydbUr79iybFYhxlWOKnFXqYlsp07JULr8',
            'grant_type': 'password'
        }
        response = requests.request('POST', self.TOKEN_URL, data=payload)
        if response.ok:
            return response.json().get("access_token")
        else:
            raise Exception(f"invalid credentials or internal error: {response.json()}")

    async def speech_to_text(self, file_path):
        file_path = f'{file_path}.wav'
        url = "https://api.aipaa.ir/api/v1/voice/asr/?asr_mode=shiva&lang_boost=fast"
        files = [
            ('file', open(file_path, 'rb'))
        ]
        response = requests.request('POST', url, headers=self.headers, files=files)

        response_bytes = response.text.encode('utf8')
        response_str = response_bytes.decode('utf-8')
        response_data = json.loads(response_str)
        if response_data['transcripts']:
            transcription = response_data['transcripts'][0]
        else:
            logger.info(response_data)
            transcription = "ارتباط با هوش مصنوعی برقرار نیست"
        return transcription

    async def text_to_speech(self, text, save_path):
        payload = {'input_text': text, "sample_rate": 22050, "compress": True, "speed": 1}
        response = requests.post(self.TTS_URL, headers=self.headers, data=payload)
        mp3_file = f'{save_path}.mp3'
        wav_file = f'{save_path}.wav'
        if response.status_code == 200:
            data = response.json()
            download_result = await self.download_audio(data.get("file_id"), mp3_file )
            await self.convert_mp3_to_wav(mp3_file , wav_file)
            return download_result
        else:
            logger.error(f"Error in TTS request: {response.text}")
            return None

    async def download_audio(self, file_id, save_path):
        try:
            url = self.DOWNLOAD_URL.format(id=file_id)
            response = requests.get(url, headers=self.headers, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                return save_path
            else:
                logger.error(f"Failed to download audio: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            return None

    @staticmethod
    async def convert_mp3_to_wav(mp3_file, wav_file):
        try:
            # Load MP3 file
            audio = AudioSegment.from_mp3(mp3_file)

            # Convert to correct format for Asterisk (8kHz, Mono, 16-bit PCM)
            audio = (
                audio.set_frame_rate(8000)
                    .set_channels(1)
                    .set_sample_width(2)
            )

            # Export as WAV
            audio.export(wav_file, format="wav")

            # Remove MP3 file after successful conversion
            os.remove(mp3_file)

            logger.info(f"Successfully converted {mp3_file} to {wav_file}")
            return wav_file
        except Exception as e:
            logger.error(f"Error converting {mp3_file}: {e}")
            return None


