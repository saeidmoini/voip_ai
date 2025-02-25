import asyncio
import os
from src.logger_config import logger, PATH
from src.report_analysis import Analysis
import uuid



async def transcribe_and_converse(audio_file, report_res, aipaa_bot, aval):

    coldroom_timeout = os.path.join(PATH, "audio", "important_coldroom-timeout")

    """Function to run transcription and AI conversation in another process"""
    try:
        transcription = "رطوبت"
        #transcription = await asyncio.wait_for(aipaa_bot.speech_to_text(audio_file), timeout=10)
        logger.info(f'Transcription result: {transcription}')

        logger.info("Attempting to analyze audio...")
        status, ai_answer = await asyncio.wait_for(aval.start_conversation(transcription), timeout=10)
        if status:
            logger.info("Aval ai answer : " + ai_answer)
            report_result = await asyncio.wait_for(report_res, timeout=40)
            logger.info(report_result)
            first_key = next(iter(report_result))
            text_data = report_result[first_key]
            analysis = Analysis(text_data)
            general = analysis.general()
            if hasattr(analysis, ai_answer):  # Check if the method exists
                user_result = getattr(analysis, ai_answer)()

                final_answer = f'{user_result} همچنين {general}'
            else:
                final_answer = f' اطلاعاتي از پارامتر درخواستي شما يافت نشد همچنين{general}'

            audio_file = os.path.join(PATH, "audio", f"user_{uuid.uuid4()}")
            logger.info("Attempting to convert text to speech")
            await asyncio.wait_for(aipaa_bot.text_to_speech(final_answer, audio_file), timeout=10)
        else:
            audio_file = None
            logger.info("Aval ai answer : " + ai_answer)

        return status, audio_file

    except asyncio.TimeoutError:
        raise NotImplementedError((f"Timeout Error in function", coldroom_timeout))
    except NotImplementedError as e:
        message, value = e.args[0]
        raise NotImplementedError((message, value))
    except Exception as e:
        raise NotImplementedError((f"Error occurred in function: {e}", coldroom_timeout))
