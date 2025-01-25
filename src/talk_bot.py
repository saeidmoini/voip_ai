from pydub import AudioSegment
import logging
import os
import asyncio
import httpx
import time

logger = logging.getLogger('agi_logger')


class TalkBot:
    def __init__(self, access_token, PATH):
        self.url = 'https://api.talkbot.ir/v1/media/text-to-speech/REQ'
        self.headers = {
            'Authorization': f'Bearer {access_token}'
        }
        self.PATH = PATH

    async def text_to_speech(self, text, file_name, gender='male', server='azure', lang='persian'):
        retries = 3
        for attempt in range(retries):
            try:
                data = {
                    'text': text,
                    'gender': 'male',
                    'lang': 'persian'
                }
                speech_file_path = os.path.join(self.PATH, "logs", f"{file_name}.mp3")
                wav_file = os.path.join(self.PATH, "logs", f"{file_name}.wav")
                timeout = httpx.Timeout(15.0, read=20.0)  # Increased timeout

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(self.url, headers=self.headers, data=data)
                    if response.status_code == 200:
                        response_data = response.json()
                        download_url = response_data.get("response", {}).get("download")
                        if download_url:
                            print(f'Download URL: {download_url}')
                            await self.download_file(download_url, speech_file_path)
                            await self.convert_mp3_to_wav(speech_file_path, wav_file)
                            break  # Exit loop if successful
                        else:
                            print("Download URL not found in the response.")
                            return None
                    else:
                        print(f'Error: {response.status_code} - {response.text}')
                        return None
                return True

            except httpx.ReadTimeout:
                print(f"Request timed out. Attempt {attempt + 1}/{retries}. Retrying...")
                time.sleep(2)  # Wait before retrying
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                return None
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                return None
        return None  # If retries fail

    @staticmethod
    async def download_file(url, file_path):
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                with open(file_path, "wb") as file:
                    async for chunk in response.aiter_bytes():
                        file.write(chunk)

    @staticmethod
    async def convert_mp3_to_wav(mp3_file, wav_file):
        try:
            # Load the MP3 file
            audio = AudioSegment.from_mp3(mp3_file)
            audio = audio.set_frame_rate(8000)
            # Export the audio as a WAV file
            audio.export(wav_file, format="wav")
            os.remove(mp3_file)
            logger.info(f"Successfully converted {mp3_file} to {wav_file}")
        except Exception as e:
            logger.info(f"Error converting {mp3_file}: {e}")
