#!/opt/voip_ai/venv/bin/python


import os
import random
import asyncio
from src.functions import transcribe_and_converse, app_start, seller_senario
from src.logger_config import logger, PATH
from src.sms_report import Report
import uuid
from src.utils import handle_timeout_or_failure
from config import tts_token, stt_token, Avalai_API
#from asterisk.agi import AGI
from src.fake_agi import FakeAGI
AGI = FakeAGI
from src.openai_module import AvalAiApi
from src.vira import ViraSpeechAPI
from app import generate_invoice

async def random_hello(user_name):
    # پیشوند ثابت
    prefix = "سلام "

    # لیست کلمات بدون اسم (تکی)
    prefix_words = ["عزیزدل", "دلبندم", "گلم", "قشنگم", "سرورم", "عزیزم", "نازنینم", "رییس"]

    # لیست پسوندها بدون اسم
    suffixes = ["بزرگوار", "ارجمند", "عزیز", "نازنین", "دوست داشتنی"]

    # انتخاب رندوم از لیست‌ها
    use_name = random.choice([True, False])  # تعیین اینکه اسم و پسوند نمایش داده بشه یا فقط کلمه بدون اسم
    if use_name:
        suffix = random.choice(suffixes)  # انتخاب پسوند رندوم و اضافه کردن اسم کاربر به آن
        greeting = f"{prefix} {user_name} {suffix}"
    else:
        greeting = f"{prefix} {random.choice(prefix_words)}"

    return greeting

async def main():
    agi = AGI()
    agi.answer()
    agi.verbose("App Started")
    phone = agi.get_variable("CALLERID(num)")
    phone = "0" + phone[2:]

    onhold = os.path.join(PATH, "audio", "important_hold")
    wellcome = os.path.join(PATH, "audio", "important_wellcome")
    coldroom_timeout = os.path.join(PATH, "audio", "important_coldroom-timeout")
    error_voice = os.path.join(PATH, "audio", "important_error")
    wait = os.path.join(PATH, "audio", "important_wait")
    ask_again = os.path.join(PATH, "audio", "important_ask-again")
    multi_wellcome = os.path.join(PATH, "audio", "important_multi_wellcome")
    city_found = os.path.join(PATH, "audio", "important_city_found")
    city_lost = os.path.join(PATH, "audio", "important_city_lost")
    goodby = os.path.join(PATH, "audio", "important_goodby")
    seller_hi = os.path.join(PATH, "audio", "important_seller_hi")
    invoice_sent = os.path.join(PATH, "audio", "important_invoice_sent")

    roll = "admin"
    try:
        vira = ViraSpeechAPI(stt_token=stt_token, tts_token=tts_token)

        report = Report(phone)
        user_info = await asyncio.wait_for(report.init_async(), timeout=5)
        if not user_info.exists():
            roll = "customer"
            aval = AvalAiApi(Avalai_API, "customer")


        if roll == "admin":
            aval = AvalAiApi(Avalai_API, "admin")

            user_list = list(user_info)
            logger.info("Attempting to authenticate with vira bot...")
            hi_text = await random_hello(user_list[0].name)

            # start_app = asyncio.create_task(app_start(vira, hi_text))
            # while not start_app.done():
            #     logger.info("Start Onhold")
            #     await asyncio.to_thread(agi.stream_file, onhold)  # Play on-hold audio
            #     await asyncio.sleep(1)

            # audio_file = await start_app
            # await asyncio.to_thread(agi.stream_file, audio_file)

    except asyncio.TimeoutError:
        await handle_timeout_or_failure(agi, coldroom_timeout, f"Timeoute Error in main 1")
    except NotImplementedError as e:
        message, value = e.args[0], e.args[1]
        await handle_timeout_or_failure(agi, value, message)
    except Exception as e:
        await handle_timeout_or_failure(agi, coldroom_timeout, f"Error occurred in main 1: {e}")

    if roll == "admin":
        try:
            if len(user_list) > 1:
                await asyncio.to_thread(agi.stream_file, multi_wellcome)
                while True:
                    recording_file = os.path.join(PATH, "audio", f"recording_{uuid.uuid4()}")
                    agi.record_file(recording_file, 'wav', '#')
                    await asyncio.to_thread(agi.stream_file, wait)

                    transcription = "گرگان"
                    #transcription = await asyncio.wait_for(vira.speech_to_text(recording_file), timeout=25)
                    logger.info(f'Transcription result: {transcription}')
                    logger.info("Attempting to analyze audio...")
                    city = report.check_city(transcription)
                    if city:
                        logger.info("My ai answer : " + city)
                        report_res = asyncio.create_task(report.get_reports())
                        await asyncio.to_thread(agi.stream_file, city_found)
                        break
                    else:
                        await asyncio.to_thread(agi.stream_file, city_lost)
            else:
                report_res = asyncio.create_task(report.get_reports())
                await asyncio.to_thread(agi.stream_file, wellcome)

        except asyncio.TimeoutError:
            await handle_timeout_or_failure(agi, coldroom_timeout, f"Timeoute Error in main 2")
        except NotImplementedError as e:
            message, value = e.args[0], e.args[1]
            await handle_timeout_or_failure(agi, value, message)
        except Exception as e:
            await handle_timeout_or_failure(agi, coldroom_timeout, f"Error occurred in main 2: {e}")

        while True:
            recording_file = os.path.join(PATH, "audio", f"recording_{uuid.uuid4()}")
            agi.record_file(recording_file, 'wav', '#')
            transcribe_chat = asyncio.create_task(transcribe_and_converse(recording_file, report_res, vira, aval))
            await asyncio.to_thread(agi.stream_file, wait)
            try:
                while not transcribe_chat.done():
                    logger.info("Start Onhold")
                    await asyncio.to_thread(agi.stream_file, onhold)  # Play on-hold audio
                    await asyncio.sleep(1)  # Prevent blocking other tasks

                status, final_answer_file = await transcribe_chat
                if status:
                    await asyncio.to_thread(agi.stream_file, final_answer_file)
                else:
                    await asyncio.to_thread(agi.stream_file, goodby)
                    break

            except NotImplementedError as e:
                message, value = e.args[0], e.args[1]
                await handle_timeout_or_failure(agi, value, message)
            except Exception as e:
                await handle_timeout_or_failure(agi, coldroom_timeout, f"Error occurred in main 3: {e}")

    elif roll == "customer":

        logger.info("seller hi")
        #introduce = os.path.join(PATH, "audio", "introduce")
        #await asyncio.wait_for(vira.text_to_speech("من سعید معینی هستم و یک سرد خونه زیر صفر 20 تنی میخوام", invoice_sent), timeout=10)
        await asyncio.to_thread(agi.stream_file, seller_hi)
        while True:
            recording_file = os.path.join(PATH, "audio", f"recording_{uuid.uuid4()}")
            agi.record_file(recording_file, 'wav', '#')

            transcribe_chat = asyncio.create_task(seller_senario(recording_file, vira, aval))
            await asyncio.to_thread(agi.stream_file, wait)
            try:
                while not transcribe_chat.done():
                    logger.info("Start Onhold")
                    await asyncio.to_thread(agi.stream_file, onhold)  # Play on-hold audio
                    await asyncio.sleep(1)  # Prevent blocking other tasks

                status, final_answer_file = await transcribe_chat
                logger.info(final_answer_file)

                if status:
                    await asyncio.to_thread(agi.stream_file, final_answer_file)
                else:
                    name = final_answer_file["name"]
                    storage_type = final_answer_file["storage_type"]
                    tonnage = final_answer_file["tonnage"]
                    result = await asyncio.wait_for(generate_invoice(name, phone, storage_type, tonnage, True), timeout=15)
                    logger.info(result)
                    await asyncio.to_thread(agi.stream_file, invoice_sent)
                    break
            except NotImplementedError as e:
                message, value = e.args[0], e.args[1]
                await handle_timeout_or_failure(agi, value, message)
            except Exception as e:
                await handle_timeout_or_failure(agi, error_voice, f"Error occurred in customer senario: {e}")

    agi.hangup()


if __name__ == "__main__":
    asyncio.run(main())
