import asyncio
import json
from datetime import datetime
import requests
from config import PHONE_MELIPAYAMAK, logger
from model import User, CachedValue


class Report:
    def __init__(self, phone):
        self.phone = phone
        self.phone_check = True
        self.coldrooms_phone_list = []
        self.reports = {}
        self.user = User.select(User.coldrooms_phone).where(
            (User.telephone.contains(self.phone))
        )
        if not self.user:
            self.phone_check = False

    def send_message(self):
        data = {'from': PHONE_MELIPAYAMAK, 'to': self.coldrooms_phone_list, 'text': 'Report', 'udh': ''}
        response = requests.post('https://console.melipayamak.com/api/send/advanced/bdee1f57c9eb4e7498e28cb9293eee07',
                                 json=data)

        try:
            data = json.loads(response.text)
            print("JSON معتبر دریافت شد:", data)
        except json.JSONDecodeError as e:
            print("خطای JSON:", e)

    async def get_reports(self):
        for user in self.user:
            PhonCool = user.coldrooms_phone
            PhonCool = PhonCool.lstrip("0")
            self.coldrooms_phone_list.append(PhonCool)

        self.send_message()
        try:
            await asyncio.wait_for(
                self.get_messages_loop(),
                timeout=60
            )
            return self.reports
        except asyncio.TimeoutError:
            return "Timeout"

    async def get_messages_loop(self):
        now = CachedValue()

        while True:
            await self.get_messages(now)
            await asyncio.sleep(1)
            if len(self.reports) >= len(self.coldrooms_phone_list):
                return False

    async def get_messages(self, now):
        data = {'type': 'in', 'number': PHONE_MELIPAYAMAK, 'index': 0, 'count': 10}
        response = requests.post(
            'https://console.melipayamak.com/api/receive/messages/bdee1f57c9eb4e7498e28cb9293eee07',
            json=data)
        data = json.loads(response.text)
        for item in data["messages"]:
            datetime_object = datetime.strptime(item['sendDate'], "%Y-%m-%dT%H:%M:%S.%f")
            if datetime_object > now.get_value() and item['sender'] in self.coldrooms_phone_list:
                self.reports[item['sender']] = item["body"]
