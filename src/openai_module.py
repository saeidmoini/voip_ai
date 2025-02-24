import asyncio
from langchain_openai import ChatOpenAI
import os
from src.logger_config import logger, PATH

avalai_error = os.path.join(PATH, "audio", "important_avalai_error")

class AvalAiApi:
    def __init__(self, API_KEY):
        self.API_KEY = API_KEY
        self.chat = ChatOpenAI(
            model="gpt-4o-mini",
            base_url="https://api.avalai.ir/v1",
            api_key=self.API_KEY,
            temperature=0
        )

        self.messages = [
            {"role": "system",
             "content": "شما یک دستیار هوشمند هستید که به کاربر کمک می‌کنید تا اطلاعات سردخانه خود را دریافت کند. "
                        "اطلاعات شامل رطوبت (HUM1)، وضعیت برق (Vbat)، دما (TEMP1) و شارژ سیم‌کارت (Credit) می‌شود. "
                        "اگر کاربر یکی از این موارد را درخواست کرد، فقط کد انگلیسی آن را برگردانید (HUM1، Vbat، TEMP1 یا Credit). "
                        "اگر کاربر چیزی غیر از این موارد پرسید، به صورت روان و فارسی (اصلا از کلمات انگلیسی استفاده نکن) "
                        "به او کمک کنید تا یکی از این موارد را انتخاب کند."}
        ]
        self.components = {
            "رطوبت": "HUM1",
            "وضعیت برق": "Vbat",
            "دما": "TEMP1",
            "شارژ سیم‌کارت": "Credit"
        }
        self.max_messages = 5  # To prevent excessive memory usage

    async def start_conversation(self, user_input):
        """Handles user input, sends it to AI, and returns the recognized command or response."""
        try:
            self.messages.append({"role": "user", "content": user_input})

            # Ensure messages list doesn't grow indefinitely
            if len(self.messages) > self.max_messages:
                self.messages.pop(1)  # Remove oldest user message (keep system message)

            # Set a timeout for AI response
            response = await asyncio.wait_for(
                asyncio.to_thread(self.chat.invoke, self.messages), timeout=8
            )

            if not response or not hasattr(response, "content"):
                raise ValueError("Invalid response received from Aval-AI.")

            assistant_reply = response.content
            self.messages.append({"role": "assistant", "content": assistant_reply})

            status, answer_analys = self.analyze_user_input(assistant_reply)
            return status, answer_analys

        except asyncio.TimeoutError:
            raise NotImplementedError(("Aval Ai Timeout ERROR", avalai_error))
        except Exception as e:
            raise NotImplementedError((f"AvalAi Exception: {str(e)}", avalai_error))

    def analyze_user_input(self, assistant_reply):
        """Analyzes the AI response to detect the requested information."""
        for component, word in self.components.items():
            if word in assistant_reply:
                return True, word
        return None, assistant_reply
