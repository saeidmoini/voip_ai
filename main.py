#!/root/voip_ai/venv/bin/python


import os
import asyncio
#from asterisk.agi import AGI
from src.fake_agi import FakeAGI
AGI = FakeAGI
from src.functions import transcribe_and_converse
from src.logger_config import logger, PATH
from src.sms_report import Report
import uuid
from src.utils import handle_timeout_or_failure
from config import Aipaa_API, Avalai_API
from src.aipaa import Aipaa
from src.openai_module import AvalAiApi

async def main():
    agi = AGI()
    agi.answer()
    agi.verbose("App Started")
    phone = agi.get_variable("CALLERID(num)")
    phone = "0" + phone[2:]

    onhold = os.path.join(PATH, "audio", "important_hold")
    wellcome = os.path.join(PATH, "audio", "important_wellcome")
    coldroom_timeout = os.path.join(PATH, "audio", "important_coldroom-timeout")
    wait = os.path.join(PATH, "audio", "important_wait")
    ask_again = os.path.join(PATH, "audio", "important_ask-again")
    multi_wellcome = os.path.join(PATH, "audio", "important_multi_wellcome")

    try:
        aipaa_bot = Aipaa(Aipaa_API[0], Aipaa_API[1])
        aval = AvalAiApi(Avalai_API)
        logger.info("Attempting to authenticate with Aipaa bot...")
        await asyncio.wait_for(aipaa_bot.authenticate(), timeout=10)

    except asyncio.TimeoutError:
        await handle_timeout_or_failure(agi, coldroom_timeout, f"Timeoute Error in main 1: {e}")
    except NotImplementedError as e:
        message, value = e.args[0]
        await handle_timeout_or_failure(agi, value, message)
    except Exception as e:
        await handle_timeout_or_failure(agi, coldroom_timeout, f"Error occurred in main 1: {e}")

    try:
        report = Report(phone)
        user_info = await asyncio.wait_for(report.init_async(), timeout=10)
        logger.info(user_info)
        if user_info.count() > 1:
            await asyncio.to_thread(agi.stream_file, multi_wellcome)
            recording_file = os.path.join(PATH, "audio", f"recording_{uuid.uuid4()}")
            agi.record_file(recording_file, 'wav', '#')
            transcription = "گرگان"
            # transcription = await asyncio.wait_for(aipaa_bot.speech_to_text(audio_file), timeout=10)
            logger.info(f'Transcription result: {transcription}')
            logger.info("Attempting to analyze audio...")
            status, ai_answer = await asyncio.wait_for(aval.start_conversation(transcription), timeout=10)
            if status:
                logger.info("Aval ai answer : " + ai_answer)



        else:
            report_res = asyncio.create_task(user_info.get_reports())

        await asyncio.to_thread(agi.stream_file, wellcome)

    except asyncio.TimeoutError:
        await handle_timeout_or_failure(agi, coldroom_timeout, f"Timeoute Error in main 2: {e}")
    except NotImplementedError as e:
        message, value = e.args[0]
        await handle_timeout_or_failure(agi, value, message)
    except Exception as e:
        await handle_timeout_or_failure(agi, coldroom_timeout, f"Error occurred in main 2: {e}")

    while True:
        recording_file = os.path.join(PATH, "audio", f"recording_{uuid.uuid4()}")
        agi.record_file(recording_file, 'wav', '#')
        transcribe_chat = asyncio.create_task(transcribe_and_converse(recording_file, report_res, aipaa_bot, aval))
        await asyncio.to_thread(agi.stream_file, wait)
        try:
            while not transcribe_chat.done():
                logger.info("Start Onhold")

                await asyncio.to_thread(agi.stream_file, onhold)  # Play on-hold audio
                await asyncio.sleep(1)  # Prevent blocking other tasks

            status, final_answer_file = await transcribe_chat
            if status:
                await asyncio.to_thread(agi.stream_file, final_answer_file)
                break
            else:
                await asyncio.to_thread(agi.stream_file, ask_again)
        except NotImplementedError as e:
            message, value = e.args[0]
            await handle_timeout_or_failure(agi, value, message)
        except Exception as e:
            await handle_timeout_or_failure(agi, coldroom_timeout, f"Error occurred in main 3: {e}")

    agi.hangup()

if __name__ == "__main__":
    asyncio.run(main())
