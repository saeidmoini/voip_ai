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

    report = Report(phone)
    await asyncio.wait_for(report.init_async(), timeout=10)
    await asyncio.to_thread(agi.stream_file, wellcome)

    while True:
        recording_file = os.path.join(PATH, "audio", f"recording_{uuid.uuid4()}")
        agi.record_file(recording_file, 'wav', '#')
        transcribe_chat = asyncio.create_task(transcribe_and_converse(recording_file, report.start))
        await asyncio.to_thread(agi.stream_file, wait)
        try:
            while not transcribe_chat.done():
                logger.info("Start Onhold")

                await asyncio.to_thread(agi.stream_file, onhold)  # Play on-hold audio
                await asyncio.sleep(10)  # Prevent blocking other tasks

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
            await handle_timeout_or_failure(agi, coldroom_timeout, f"Error occurred in main : {e}")

    agi.hangup()

if __name__ == "__main__":
    asyncio.run(main())
