#!/root/voip_ai/venv/bin/python


import os
import sys
import asyncio
from datetime import datetime

from config import Avalai_API, Aipaa_API, DEEP_SEEK_API
from asterisk.agi import AGI
from src.openai_module import AvalAiApi
from src.aipaa import Aipaa
from src.functions import Report
from src.report_analysis import Analysis
from src.logger_config import logger, PATH
from src.deep_seek import DeepSeek


async def main():

    # agi = AGI()
    # agi.answer()
    aipaa_bot = Aipaa(Aipaa_API[0], Aipaa_API[1])
    deep = DeepSeek(DEEP_SEEK_API)
    aval = AvalAiApi(Avalai_API)
    # agi.verbose("App Started")
    phone = "989369344330"
    phone = "0" + phone[2:]
    report = Report(phone)
    onhold = os.path.join(PATH, "audio", "hold")
    wellcome = os.path.join(PATH, "audio", "wellcome")
    coldroom_timeout = os.path.join(PATH, "audio", "coldroom-timeout")

    if report.phone_check:
        report_res = asyncio.create_task(report.get_reports())
    else:
        phone_notfound = os.path.join(PATH, "audio", "PhoneNotFound")
        # agi.stream_file(phone_notfound)
        # agi.hangup()
        logger.info("Phone Dosent Exist")
        sys.exit()
        return

    # agi.stream_file(wellcome)
    logger.info("Wellcome")
    while True:
        audio_file = os.path.join(PATH, "audio", "recording")
        # agi.record_file(audio_file, 'wav', '#')
        #transcription = await aipaa_bot.speech_to_text(audio_file)
        transcription = "دمای سردخونه چنده"
        logger.info(f'before aval : {datetime.now()}')
        status, ai_answer = await aval.start_conversation(transcription)
        logger.info(f'after aval : {datetime.now()}')
        status, ai_answer = await deep.start_conversation(transcription)
        logger.info(f'after deep : {datetime.now()}')
        if status:
            logger.info(ai_answer)
            break
        else:
            logger.info(ai_answer)
            audio_file = os.path.join(PATH, "audio", "user")
            #result = await aipaa_bot.text_to_speech(ai_answer, audio_file)
            # agi.stream_file(audio_file)

    try:
        asyncio_result = await asyncio.wait_for(report_res, timeout=60)
    except asyncio.TimeoutError:
        logger.info("Coldroom's Timeout")

        # agi.stream_file(coldroom_timeout)
        # agi.hangup()
        sys.exit()
        return

    first_key = next(iter(asyncio_result))
    text_data = asyncio_result[first_key]
    logger.info(text_data)
    analysis = Analysis(text_data)
    if asyncio_result:
        relays = analysis.relays()
        inputs = analysis.inputs()
        if hasattr(analysis, ai_answer):  # Check if the method exists
            user_result = getattr(analysis, ai_answer)()

            final_answer = f'{relays} همچنین {inputs} همچنین {user_result}'
        else:
            final_answer = f'{relays} همچنین {inputs} اطلاعاتی از پارامتر درخواستی شما یافت نشد '

        audio_file = os.path.join(PATH, "audio", "user")
        result = await aipaa_bot.text_to_speech(final_answer, audio_file)
        #agi.stream_file(audio_file)
    else:
        # agi.stream_file(coldroom_timeout)
        # agi.hangup()
        sys.exit()


async def start_call():
    agi = AGI()
    agi.answer()
    aipaa_bot = Aipaa(Aipaa_API[0], Aipaa_API[1])
    #aval = AvalAiApi(Avalai_API)
    deep = DeepSeek(DEEP_SEEK_API)
    agi.verbose("App Started")
    phone = agi.get_variable("CALLERID(num)")
    phone = "0" + phone[2:]
    report = Report(phone)
    onhold = os.path.join(PATH, "audio", "hold")
    wellcome = os.path.join(PATH, "audio", "wellcome")
    coldroom_timeout = os.path.join(PATH, "audio", "coldroom-timeout")
    wait = os.path.join(PATH, "audio", "wait")

    if report.phone_check:
        report_res = asyncio.create_task(report.get_reports())
    else:
        phone_notfound = os.path.join(PATH, "audio", "PhoneNotFound")
        logger.info("Phone Dosent Exist")
        agi.stream_file(phone_notfound)
        agi.hangup()
        sys.exit()
        return

    agi.stream_file(wellcome)
    while True:
        audio_file = os.path.join(PATH, "audio", "recording")
        agi.record_file(audio_file, 'wav', '#')
        agi.stream_file(wait)
        agi.stream_file(onhold)
        transcription = await aipaa_bot.speech_to_text(audio_file)
        try:
            status, ai_answer = await asyncio.wait_for(deep.start_conversation(transcription),
                                                       timeout=15)  # Set timeout as needed
        except asyncio.TimeoutError:
            logger.info("start_conversation timed out")
            agi.stream_file(coldroom_timeout)
            agi.hangup()
            sys.exit()

        if status:
            logger.info(ai_answer)
            break
        else:
            logger.info(ai_answer)
            audio_file = os.path.join(PATH, "audio", "user")
            result = await aipaa_bot.text_to_speech(ai_answer, audio_file)
            if result:
                agi.stream_file(audio_file)
            else:
                logger.info('text to speech failed')
                logger.info(result)

    try:
        asyncio_result = await asyncio.wait_for(report_res, timeout=60)
    except asyncio.TimeoutError:
        logger.info("Coldroom's Timeout")
        agi.stream_file(coldroom_timeout)
        agi.hangup()
        sys.exit()
    logger.info(asyncio_result)
    first_key = next(iter(asyncio_result))
    text_data = asyncio_result[first_key]
    logger.info(text_data)
    analysis = Analysis(text_data)
    if asyncio_result:
        relays = analysis.relays()
        inputs = analysis.inputs()
        if hasattr(analysis, ai_answer):  # Check if the method exists
            user_result = getattr(analysis, ai_answer)()

            final_answer = f'{user_result} همچنین {inputs} همچنین {relays}'
        else:
            final_answer = f' اطلاعاتی از پارامتر درخواستی شما یافت نشد همچنین{relays} و همچنین {inputs}'

        audio_file = os.path.join(PATH, "audio", "user")
        result = await aipaa_bot.text_to_speech(final_answer, audio_file)
        agi.stream_file(audio_file)
    else:
        agi.stream_file(coldroom_timeout)
        agi.hangup()
        sys.exit()


if __name__ == "__main__":
    # asyncio.run(start_call())
    asyncio.run(main())
