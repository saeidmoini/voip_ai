import asyncio
import os
from src.logger_config import logger, PATH
from src.report_analysis import Analysis
import uuid


coldroom_timeout = os.path.join(PATH, "audio", "important_coldroom-timeout")
error_voice = os.path.join(PATH, "audio", "important_error")


async def app_start(vira, hi_text):
    try:
        audio_file = os.path.join(PATH, "audio", f"user_{uuid.uuid4()}")
        logger.info("Attempting to convert text to speech")
        await asyncio.wait_for(vira.text_to_speech(hi_text, audio_file), timeout=25)
        return audio_file
    except asyncio.TimeoutError:
        raise NotImplementedError(f"Timeout Error in function", coldroom_timeout)
    except NotImplementedError as e:
        message, value = e.args[0], e.args[1]
        raise NotImplementedError(message, value)
    except Exception as e:
        raise NotImplementedError(f"Error occurred in function: {e}", coldroom_timeout)


async def transcribe_and_converse(audio_file, report_res, vira, aval):
    """Function to run transcription and AI conversation in another process"""
    try:
        transcription = await asyncio.wait_for(vira.speech_to_text(audio_file), timeout=25)
        logger.info(f'Transcription result: {transcription}')

        report_result = await asyncio.wait_for(report_res, timeout=30)
        first_key = next(iter(report_result))
        text_data = report_result[first_key]
        # text_data = """
        #         relays=0x003
        #         inputs=0x00
        #         M=0x5a04
        #         ADC1=0.0 v
        #         ADC2=0.0 v
        #         ADC3=0.0 v
        #         ADC4=0.0 v
        #         Vdc=11.5 v
        #         Vbat=0.0 v
        #         HUM=NC
        #         TEMP=-16.9
        #         HUM1=NC
        #         TEMP1=-17.0
        #         TEMP2=NC
        #         TEMP3=NC
        #         TEMP4=NC
        #         SIGNAL=28.0
        #         Credit=148967.5
        #         UPTIME=05:04:55
        #         Cloud=0"""
        analysis = Analysis(text_data)

        logger.info("Attempting to analyze audio...")
        status, ai_answer = await asyncio.wait_for(aval.start_conversation(transcription, analysis.lines), timeout=25)
        if status:
            logger.info("Aval ai answer : " + ai_answer)
            audio_file = os.path.join(PATH, "audio", f"user_{uuid.uuid4()}")
            logger.info("Attempting to convert text to speech")
            await asyncio.wait_for(vira.text_to_speech(ai_answer, audio_file), timeout=25)
        else:
            audio_file = None
            logger.info("Aval ai answer : " + ai_answer)

        return status, audio_file

    except asyncio.TimeoutError:
        raise NotImplementedError(f"Timeout Error in function", coldroom_timeout)
    except NotImplementedError as e:
        message, value = e.args[0], e.args[1]
        raise NotImplementedError(message, value)
    except Exception as e:
        raise NotImplementedError(f"Error occurred in function: {e}", coldroom_timeout)

async def seller_senario(audio_file, vira, aval):
    """Function to run transcription and AI conversation in another process"""
    try:
        #transcription = ' سلام من سعید معینی هستم و دستگاه بیست تن برای سرد خونه زیر صفر میخوام'
        transcription = await asyncio.wait_for(vira.speech_to_text(audio_file), timeout=25)
        logger.info(f'Transcription result: {transcription}')

        status, ai_answer = await asyncio.wait_for(aval.start_conversation(transcription), timeout=25)
        if status:
            logger.info("Aval ai answer : " + ai_answer)
            answer = os.path.join(PATH, "audio", f"user_{uuid.uuid4()}")
            logger.info("Attempting to convert text to speech")
            await asyncio.wait_for(vira.text_to_speech(ai_answer, answer), timeout=25)
        else:
            answer = ai_answer
        return status, answer

    except asyncio.TimeoutError:
        raise NotImplementedError(f"Timeout Error in function", error_voice)
    except NotImplementedError as e:
        message, value = e.args[0], e.args[1]
        raise NotImplementedError(message, value)
    except Exception as e:
        raise NotImplementedError(f"Error occurred in function: {e}", error_voice)