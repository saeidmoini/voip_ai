#!/root/voip_ai/venv/bin/python
import time
import os
import asyncio
from config import Avalai_API, logger, PATH, Talkbot_API
from asterisk.agi import AGI
from src.audio import record_audio
from src.openai_module import AvalAiApi, prompt
#from src.talk_bot import TalkBot
#from src.asure import AzureTTS


async def main():
    logger.info("App Started")


async def start_call():
    start = time.time()

    # Talk_Bot = TalkBot(Talkbot_API, PATH)
    Avalai_Api = AvalAiApi(Avalai_API, PATH)
    # azure_tts = AzureTTS(subscription_key="sk-69a9bec33dedd7311f91cb78d60d849c", region="westeurope", path=PATH)

    # agi = AGI()
    # agi.answer()

    # Hello World
    # text = 'سلام! به ویپ هوشمند خوش آمدید. برای شروع، لطفاً پس از شنیدن صدای بوق، کد سردخونه را اعلام کنید و زمانی که صحبت شما تمام شد، حتماً کلید مربع را فشار دهید'
    # tts = await Talk_Bot.text_to_speech(text, 'hello')
    # await azure_tts.text_to_speech(text, "azure_test")

    print(f"Task duration: {time.time() - start} seconds")
    hello_file = os.path.join(PATH, "logs", "hello")
    # agi.stream_file(hello_file)
    # Record User Audio
    audio_file = os.path.join(PATH, "logs", "recording")
    # record_audio(agi, audio_file)

    transcription = await Avalai_Api.stt(audio_file + '.wav')
    logger.info(transcription)

    # transcription = " یک, دو, سه, چهار"
    answer = await Avalai_Api.chatting(prompt(transcription))
    if answer.isdigit():
        persian_representation = number_to_persian_words(answer)
        tts = await Avalai_Api.text_to_speech(f' کُد شما {persian_representation}  میباشد ', 'user')
        wav_file = os.path.join(PATH, "logs", "user")
        # agi.stream_file(wav_file)

    logger.info(answer)
    # agi.verbose("python agi Done")
    # agi.hangup()

def number_to_persian_words(number):
    """
    Converts a number to its Persian words representation.
    For example, 1234 -> "یک، دو، سه، چهار"
    """
    persian_digits = {
        '0': 'صفر', '1': 'یک', '2': 'دو', '3': 'سه', '4': 'چهار',
        '5': 'پنج', '6': 'شش', '7': 'هفت', '8': 'هشت', '9': 'نه'
    }

    # Convert the number to a string and map each digit to its Persian equivalent
    return '، '.join(persian_digits[digit] for digit in str(number))


if __name__ == "__main__":
    asyncio.run(main())
