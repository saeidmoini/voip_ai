import asyncio
import json
from datetime import datetime
import requests
from config import PHONE_MELIPAYAMAK, logger
from model import database, User, CachedValue


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
        response = requests.post('https://console.melipayamak.com/api/send/advanced/162e19ebd29b48b0a87f76b0cd485f9f',
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

        # send_message()
        try:
            await asyncio.wait_for(
                self.get_messages_loop(),
                timeout=30
            )
            return self.reports
        except asyncio.TimeoutError:
            return False

    async def get_messages_loop(self):
        now = CachedValue()

        while True:
            await self.get_messages(now)
            await asyncio.sleep(1)
            if len(self.reports) >= len(self.coldrooms_phone_list):
                return False

    async def get_messages(self, now):
        data = {'type': 'in', 'number': PHONE_MELIPAYAMAK, 'index': 0, 'count': 4}
        response = requests.post(
            'https://console.melipayamak.com/api/receive/messages/162e19ebd29b48b0a87f76b0cd485f9f',
            json=data)
        data = json.loads(response.text)
        for item in data["messages"]:
            datetime_object = datetime.strptime(item['sendDate'], "%Y-%m-%dT%H:%M:%S.%f")
            if datetime_object > now.get_value() and item['sender'] in self.coldrooms_phone_list:
                self.reports[item['sender']] = item["body"]

    def coldroom_exist(self, code):
        print(code)
        # coldroom = self.user.where(
        #     User.coldrooms_code.contains(code)
        # )
        # if coldroom:
        #     return coldroom
        # else:
        #     return False
