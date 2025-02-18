import asyncio
import json
from datetime import datetime
from config import PHONE_MELIPAYAMAK, Melipayamak_API
from src.logger_config import logger, PATH
from src.model import User
import aiohttp


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

    async def send_message(self):
        data = {'from': PHONE_MELIPAYAMAK, 'to': self.coldrooms_phone_list, 'text': 'Report', 'udh': ''}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'https://console.melipayamak.com/api/send/advanced/{Melipayamak_API}', json=data
            ) as response:
                try:
                    response_data = await response.json()
                    logger.info(f"JSON received successfully:{response_data}")
                    return True
                except json.JSONDecodeError as e:
                    logger.info("JSON error:", e)
                    return False

    async def get_reports(self):
        for user in self.user:
            PhonCool = user.coldrooms_phone
            PhonCool = PhonCool.lstrip("0")
            self.coldrooms_phone_list.append(PhonCool)

        result = await self.send_message()
        if result:
            await self.get_messages_loop()
        if self.reports:
            return self.reports
        else:
            return None

    async def get_messages_loop(self):
        now = datetime.now()
        while True:

            await self.get_messages(now)
            if len(self.reports) >= len(self.coldrooms_phone_list):
                return False
            await asyncio.sleep(1)

    async def get_messages(self, now):
        data = {'type': 'in', 'number': PHONE_MELIPAYAMAK, 'index': 0, 'count': 4}
        logger.info(now)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f'https://console.melipayamak.com/api/receive/messages/{Melipayamak_API}', json=data
            ) as response:
                response_data = await response.json()
                for item in response_data.get("messages", []):
                    datetime_object = datetime.strptime(item['sendDate'], "%Y-%m-%dT%H:%M:%S.%f")

                    if datetime_object > now and item['sender'] in self.coldrooms_phone_list:
                        self.reports[item['sender']] = item["body"]
                return True
