from src.logger_config import logger, PATH
import asyncio
import os
from langchain_openai import ChatOpenAI


class AvalAiApi:
    def __init__(self, API_KEY):
        self.API_KEY = API_KEY
        self.chat = ChatOpenAI(model="gpt-3.5-turbo", base_url="https://api.avalai.ir/v1", api_key=self.API_KEY, temperature=0)

        self.messages = [
            {"role": "system",
             "content": "شما یک دستیار هوشمند هستید که به کاربر کمک می‌کنید تا اطلاعات سردخانه خود را دریافت کند. اطلاعات شامل رطوبت (HUM1)، وضعیت برق (Vbat)، دما (TEMP1) و شارژ سیم‌کارت (Credit) می‌شود. اگر کاربر یکی از این موارد را درخواست کرد، فقط کد انگلیسی آن را برگردانید (HUM1، Vbat، TEMP1 یا Credit). اگر کاربر چیزی غیر از این موارد پرسید، به صورت روان و فارسی (اصلا از کلمات انگلیسی استفاده نکن) به او کمک کنید تا یکی از این موارد را انتخاب کند."}
        ]
        self.components = {
            "رطوبت": "HUM1",
            "وضعیت برق": "Vbat",
            "دما": "TEMP1",
            "شارژ سیم‌کارت": "Credit"
        }

    async def start_conversation(self, user_input):
        """ Sends a request to DeepSeek API and returns the appropriate component code. """
        self.messages.append({"role": "user", "content": user_input})

        response = self.chat.invoke(self.messages)

        assistant_reply = response.content
        self.messages.append({"role": "assistant", "content": response.content})

        status, answer_analys = self.analyze_user_input(assistant_reply)
        return status, answer_analys

    def analyze_user_input(self, assistant_reply):
        """
        تحلیل متن کاربر با کمک هوش مصنوعی برای تشخیص درخواست.
        """
        # بررسی هر کلمه در متن کاربر
        for component, word in self.components.items():
            if word in assistant_reply:
                return True, word
        return None, assistant_reply



