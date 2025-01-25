from openai import OpenAI
import logging
import asyncio
import os
from pydub import AudioSegment
from langchain_openai import ChatOpenAI

logger = logging.getLogger('agi_logger')


def prompt(transcription):
    prompt_str =f"""
    متن زیر را بررسی کن و اگر کدی (عدد) در آن هست، فقط آن عدد را به‌صورت یک عدد صحیح بازگردان.
    در صورتی که کد به‌صورت اعداد جداگانه (مثلاً "یک، دو، سه، چهار") ذکر شده باشد، آن‌ها را به یک عدد کامل ترکیب کن (مثلاً "یک، دو، سه، چهار" = "1234").
    اگر عددی وجود ندارد، فقط این جمله را بازگردان: "لطفا دوباره تلاش کنید".

    مثال‌ها:
    - متن: "کد من یک دو سه چهار است" -> 1234
    - متن: "کد: دو پنج صفر" -> 250
    - متن: "هیچ عددی اینجا نیست" -> پاسخ: لطفا دوباره تلاش کنید
    - متن: "کد من هفت هزار و بیست و یک است" -> 7021
    - متن: "کد من ۹ ۸ ۷ ۶ است" -> 9876

    متن: {transcription}
    """
    return prompt_str


class AvalAiApi:
    def __init__(self, API_KEY, PATH):
        self.client = OpenAI(
            base_url="https://api.avalai.ir/v1",
            api_key=API_KEY
        )
        self.API_KEY = API_KEY
        self.PATH = PATH
        self.history = []

    async def stt(self, audio_file):
        logger.info(f"Sending {audio_file} for API")

        with open(audio_file, "rb") as audio:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text",
                language="fa"
            )
        return transcription

    async def text_to_speech(self, text, file_name):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=text,
        )
        speech_file_path = os.path.join(self.PATH, "logs", f"{file_name}.mp3")
        wav_file = os.path.join(self.PATH, "logs", f"{file_name}.wav")
        response.stream_to_file(speech_file_path)
        await asyncio.to_thread(self.convert_mp3_to_wav, speech_file_path, wav_file)


    @staticmethod
    def convert_mp3_to_wav(mp3_file, wav_file):
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

    async def chatting(self, text):
        # Append the new message to history
        chat = ChatOpenAI(model="gpt-3.5-turbo", base_url="https://api.avalai.ir/v1", api_key=self.API_KEY, temperature=0 )
        self.history.append({"role": "user", "content": text})
        # Call the API with the entire conversation history
        response = chat.invoke(self.history)
        # Append AI's response to the history
        self.history.append({"role": "assistant", "content": response.content})
        return response.content.strip()

