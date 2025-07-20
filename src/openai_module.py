import asyncio
from langchain_openai import ChatOpenAI
import os
from src.logger_config import logger, PATH
from src.payment_report import PaymentSms
import re

avalai_error = os.path.join(PATH, "audio", "important_avalai_error")


class AvalAiApi:
    def __init__(self, API_KEY, senario):
        self.API_KEY = API_KEY
        self.chat = ChatOpenAI(
            model="o4-mini",
            base_url="https://api.avalapis.ir/v1",
            api_key=self.API_KEY,
            temperature=0
        )
        self.senario = senario
        if senario == "admin":
            self.messages = [
                {"role": "system",
                 "content": "شما یک دستیار هوشمند هستید که اطلاعات سردخانه را تحلیل می‌کنید و به کاربر گزارش می‌دهید."
                            "اگر کاربر یکی از  موارد رطوبت (HUM1)، وضعیت برق (Vbat)، دما (TEMP1) و شارژ سیم‌کارت (Credit) را درخواست کرد، طبق دستور عمل زیر گزارش بهش بده "
                            "اگر کاربر چیزی غیر از این موارد پرسید، به صورت روان و فارسی جواب بده (اصلا از کلمات انگلیسی استفاده نکن) "
                            "\n\n### دستور عمل:\n"
                            "1. **Vbat (وضعیت برق)**: اگر مقدار آن `0.0` باشد، برق وصل و وضعیت سالن مناسب است. در غیر این صورت، برق قطع و سردخانه غیرفعال است.\n"
                            "2. **HUM1 (رطوبت)**: اگر مقدار `NC` باشد، رطوبتی وجود ندارد. در غیر این صورت، مقدار رطوبت را درصدی گزارش بده.\n"
                            "3. **TEMP1 (دما)**: دما رو به درجه بده. اگر دما بالاتر از صفر بود اخطار هم بده دمای زیر صفر افزایش یافته.\n"
                            "4. **Credit (شارژ سیم‌کارت)**: مقدار عددی اعتبار سیم‌کارت را اعلام کن.\n"
                            "5. **Relays (وضعیت دستگاه‌ها)**: بسته به مقدار، وضعیت سردخانه را اعلام کن.\n"
                            "*Relays مقادیر :* \n"
                            "0x000 = همه دستگاه های سردخانه خاموش یا در حالت اتومات \n"
                            "0x001 = کمپرسور و سالن زیر صفر روشن \n"
                            "0x004 = سیستم در حال دیفراست و برفک زدایی \n"
                            "0x008 = سالن بالای صفر روشن \n"
                            "0x007 = کلیه قسمت های زیر صفر و بالای صفر روشن و درحال کار \n"
                            "0x005 = سردخانه در حال دیفراست است \n"
                            "6. **Inputs (ورودی‌های کنترلی)**: بسته به مقدار، مشکلات احتمالی سردخانه را گزارش بده.\n"
                            "*Inputs مقادیر :* \n"
                            "0x01 = کنترل بار کمپرسور عمل کرده و سرخانه خاموش  \n"
                            "0x02 = سیستم با کمبود گاز مواجه شده و کمپرسور خاموش  \n"
                            "0x04 = حرارت بالای موتور باعث عملکرد ترمیستور حفاظتی شده و کمپرسور خاموش شده  \n"
                            "0x08 = رق ورودی سرخانه نقص دارد و باعث خاموش شدن سردخانه شده است لطفا برای رفع ایراد ورودی برق را چک کنید  \n"
                            "## اگر سردخانه در حالت دیفراست بود هیچ گزارشی از inputs دیگه نده"
                            "## کاربر اگر یکی از اون 4 تا رو درخواست کرد تو درجواب گزارش inputs و relays هم پیوست کن و بده"
                            "\n * هروقت مکالمت با کاربر تموم شد فقط کلمه exit خالی برگردون * \n"
                            "\n * مکالمه رو تا زمانی که کاربر نگفته تمومه ادامه بده و ببین درخواست دیگه ای داره یا نه * \n"
                 }
            ]
        elif senario == "customer":
            self.messages = [
                {"role": "system",
                 "content":
                    "مکالمه زیر مربوط به تماس ورودی مشتری با هدف خرید یا مشاوره درباره سردخانه است. لطفاً مکالمه را به شکلی هدایت کن که به‌طور طبیعی اطلاعات زیر را از مشتری بگیری:"
                    "\n  1. نام خانوادگی مشتری (`name = [string]`) \n"
                    "\n 2. ظرفیت سردخانه مورد نیاز مشتری به تن (`tonnage = [number]`) \n"
                    "\n 3. نوع سردخانه، آیا سردخانه زیر صفر می‌خواهد یا بالای صفر یا هردو(`storage_type = 'below_zero'` or `'above_zero'` or `'both'`) \n"
                    "\n * دومنظوره یا دومداره یا دوتکه یا بالای صفر و زیر صفر : اینا همش میشه both * \n"
                    "\n name = [string]   \n"
                    "\n tonnage = [number] \n"
                    "\n storage_type = [below_zero] or [above_zero] or [both] \n"
                    "\n تا زمان دریافت هر 3تا پارامتر مکالمه را ادامه بده تا همه اطلاعات جمع‌آوری شود. \n"
                    "\n * اگر هم این 3 تا اطلاعات رو گرفتی با فرمت گفته شده در پاسخ فقط همین 3تارو برگردون  * \n"
                    "\n اطلاعات رو به محض گرفتن با فرمت برگردون و تایید کاربر رو نگیر \n"

                 }
            ]
        self.max_messages = 15  # To prevent excessive memory usage

    async def start_conversation(self, user_input, raw_data = None):
        """Handles user input, sends it to AI, and returns the recognized command or response."""
        try:
            if self.senario == "admin":
                self.messages.append({"role": "system", "content": f"### داده‌های دریافتی از سردخانه:\n{raw_data}"})

            self.messages.append({"role": "user", "content": user_input})

            # Ensure messages list doesn't grow indefinitely
            if len(self.messages) > self.max_messages:
                self.messages.pop(1)  # Remove oldest user message (keep system message)
            #logger.info(self.messages)
            # Set a timeout for AI response
            response = await asyncio.wait_for(
                asyncio.to_thread(self.chat.invoke, self.messages), timeout=20
            )

            if not response or not hasattr(response, "content"):
                raise ValueError("Invalid response received from Aval-AI.")

            assistant_reply = response.content
            self.messages.append({"role": "assistant", "content": assistant_reply})

            status, answer_analys = self.analyze_assistant(assistant_reply)

            return status, answer_analys

        except asyncio.TimeoutError:
            raise NotImplementedError("Aval Ai Timeout ERROR", avalai_error)
        except Exception as e:
            # Check if the exception has an 'error' attribute
            if hasattr(e, "error"):
                error_data = e.error  # Extract error dictionary if available
            elif hasattr(e, "response") and hasattr(e.response, "json"):
                try:
                    error_data = e.response.json()  # Try getting JSON response if available
                except Exception:
                    error_data = None  # JSON parsing failed
            else:
                error_data = None

            if error_data and error_data.get("error", {}).get("code") == "quota_exceeded_error":
                sms_txt = (
                    "اعتبار وب سرویس aval ai به پایان رسیده است. \n"
                    "جهت تمدید وارد لینک زیر شده و حساب را شارژ نمایید: \n"
                    "https://chat.avalai.ir/platform/login \n"
                    "پسورد : voipAI@724"
                )
                send_sms = PaymentSms(sms_txt)

                await send_sms.send_reports()
                raise NotImplementedError(f"AvalAi : {str(e)}", avalai_error)

            raise NotImplementedError(f"AvalAi Exception: {str(e)}", avalai_error)

    def analyze_assistant(self, text):
        info = extract_information(text)
        if "exit" in text:
            return None, text
        elif info["name"] and info["tonnage"] and info["storage_type"]:
            return None, info
        else:
            return True, text

def extract_information(text):
    # Updated regex patterns
    name_pattern = r"name\s*=\s*(.+?)\s*(?:\n|$)"
    tonnage_pattern = r"tonnage\s*=\s*(\d+)"
    storage_type_pattern = r"storage_type\s*=\s*(below_zero|above_zero|both)"

    # Extracting name
    name_match = re.search(name_pattern, text, re.IGNORECASE)
    name = name_match.group(1).strip() if name_match else None

    # Extracting tonnage
    tonnage_match = re.search(tonnage_pattern, text)
    tonnage = int(tonnage_match.group(1)) if tonnage_match else None

    # Extracting storage type
    storage_type_match = re.search(storage_type_pattern, text, re.IGNORECASE)
    storage_type = storage_type_match.group(1).strip() if storage_type_match else None

    return {
        "name": name,
        "tonnage": tonnage,
        "storage_type": storage_type
    }