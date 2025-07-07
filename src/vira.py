import os
import json
import httpx
from src.logger_config import logger, PATH
from pydub import AudioSegment
from src.payment_report import PaymentSms
stt_error = os.path.join(PATH, "audio", "important_stt_error")
tts_error = os.path.join(PATH, "audio", "important_tts_error")
import traceback

class ViraSpeechAPI:
    SPEECH_TO_TEXT_URL = "https://partai.gw.isahab.ir/speechRecognition/v1/file"
    TEXT_TO_SPEECH_URL = "https://partai.gw.isahab.ir/TextToSpeech/v1/speech-synthesys"
    DOWNLOAD_URL = "http://endpoint/service/speech-synthesys/{id}"  # Placeholder

    def __init__(self, stt_token: str, tts_token: str):
        self.stt_headers = {
            'gateway-token': stt_token
        }
        self.tts_headers = {
            'Content-Type': 'application/json',
            'gateway-token': tts_token
        }

    async def speech_to_text(self, file_path: str) -> str:
        try:
            file_path += '.wav'
            async with httpx.AsyncClient(timeout=20) as client:
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f, 'audio/mpeg')}

                    response = await client.post(self.SPEECH_TO_TEXT_URL, headers=self.stt_headers, files=files)
                    if response.status_code == 400:
                        sms_txt = (
                            "اعتبار وب سرویس ویرا به پایان رسیده است. \n"
                            "جهت تمدید وارد لینک زیر شده و حساب را شارژ نمایید: \n"
                            "https://api.ivira.ai/panel/dashboard \n"
                            "پسورد : voipAI@724"
                        )
                        send_sms = PaymentSms(sms_txt)
                        await send_sms.send_reports()
                        raise Exception(response.text)
                    response.raise_for_status()
            data = response.json()
            return data['data']['data']['result']
        except Exception as e:
            logger.error("TTS Exception:\n" + traceback.format_exc())
            raise NotImplementedError(f"Speech-to-text failed: {e}", stt_error)

    async def text_to_speech(self, text: str, save_path: str, speaker: int = 3, base64: bool = False) -> dict:
        try:
            payload = {
                "data": text,
                "filePath": "true",
                "base64": "1" if base64 else "0",
                "checksum": "1",
                "speaker": str(speaker)
            }
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(self.TEXT_TO_SPEECH_URL, headers=self.tts_headers, data=json.dumps(payload))
                if response.status_code == 400:
                    sms_txt = (
                        "اعتبار وب سرویس ویرا به پایان رسیده است. \n"
                        "جهت تمدید وارد لینک زیر شده و حساب را شارژ نمایید: \n"
                        "https://api.ivira.ai/panel/dashboard \n"
                        "پسورد : voipAI@724"
                    )
                    send_sms = PaymentSms(sms_txt)
                    await send_sms.send_reports()
                    raise Exception(response.text)
                response.raise_for_status()

            mp3_file = f'{save_path}.mp3'
            wav_file = f'{save_path}.wav'
            mp3_url = f'https://{response.json()["data"]["data"]["filePath"]}'
            download_result = await self.download_audio(mp3_url, mp3_file)
            if download_result:
                self.convert_mp3_to_wav(mp3_file, wav_file)
            return mp3_url
        except Exception as e:
            raise NotImplementedError(f"Text-to-speech failed: {e}", tts_error)

    async def download_audio(self, file_url: str, save_path: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("GET", file_url) as response:
                    response.raise_for_status()

                    with open(save_path, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)

            return save_path
        except Exception as e:
            raise NotImplementedError(f"Error downloading audio from {file_url}: {e}", tts_error)

    @staticmethod
    def convert_mp3_to_wav(mp3_file, wav_file):
        try:
            audio = AudioSegment.from_mp3(mp3_file)
            audio = audio.set_frame_rate(8000).set_channels(1).set_sample_width(2)
            audio.export(wav_file, format="wav")
            os.remove(mp3_file)
            logger.info(f"Successfully converted {mp3_file} to {wav_file}")
            return wav_file
        except Exception as e:
            raise NotImplementedError(f"Error converting {mp3_file} to WAV: {e}", tts_error)
            return None





