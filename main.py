#!/root/voip_ai/venv/bin/python
import time
import os
import asyncio
from config import Avalai_API, logger, PATH
from asterisk.agi import AGI
from src.audio import record_audio
from src.openai_module import AvalAiApi
from functions import Report

async def main():
    logger.info("App Started")
    phone = "09105881921"
    report = Report(phone)

    if report.phone_check:
        report_res = asyncio.create_task(report.get_reports())
    else:
        print("no phone")
        return

    while not report_res.done():
        await asyncio.sleep(1)
    print(report_res)


async def start_call():
    start = time.time()

    Avalai_Api = AvalAiApi(Avalai_API, PATH)

    # agi = AGI()
    # agi.answer()
    phone = "09105881921"
    user = Report(phone)
    print(user.user)
    if user:
        print("t")
        #reports = asyncio.create_task(get_reports(user))
    else:
        # tts = await Avalai_Api.text_to_speech("شماره شما در سیستم ثبت نشده است", 'user')
        wav_file = os.path.join(PATH, "logs", "user")
        # agi.stream_file(wav_file)
        # agi.hangup()
        return

    #text = 'سلام! به ویپ هوشمند خوش آمدید. برای شروع، لطفاً پس از شنیدن صدای بوق، کد سردخونه را اعلام کنید و زمانی که صحبت شما تمام شد، حتماً کلید مربع را فشار دهید'
    #tts = await Avalai_Api.text_to_speech(text, 'hello')

    hello_file = os.path.join(PATH, "logs", "hello")
    # agi.stream_file(hello_file)

    audio_file = os.path.join(PATH, "logs", "recording")
    # record_audio(agi, audio_file)

    #transcription = await Avalai_Api.stt(audio_file + '.wav')
    transcription = " یک, دو, سه, چهار"
    logger.info(transcription)

    #answer = await Avalai_Api.chatting(prompt(transcription))
    answer = '1234'

    if answer.isdigit():
        persian_representation = number_to_persian_words(answer)

        #coldroom = coldroom_exist(code)
        coldroom = False
        if coldroom:
            logger.info(coldroom)
            # while not reports.done():
            #     await asyncio.sleep(1)

        #tts = await Avalai_Api.text_to_speech(f' کُد شما {persian_representation}  میباشد ', 'user')
        else:
            logger.info(coldroom)

            #tts = await Avalai_Api.text_to_speech("کد سردخانه اشتباه است لطفا دوباره تلاش کنید", 'user')

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
    #asyncio.run(start_call())

