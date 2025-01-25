import asyncio
import json
from datetime import datetime
import time

import requests
from config import PHONE_MELIPAYAMAK
from model import database, User, CachedValue

def send_message(coldrooms_phone_list):
    data = {'from': PHONE_MELIPAYAMAK, 'to': [coldrooms_phone_list], 'text': 'Report', 'udh': ''}
    response = requests.post('https://console.melipayamak.com/api/send/advanced/162e19ebd29b48b0a87f76b0cd485f9f',
                             json=data)
    # بررسی پاسخ سرور
    print("Response status code:", response.status_code)
    print("Response text:", response.text)

    try:
        data = json.loads(response.text)
        print("JSON معتبر دریافت شد:", data)
    except json.JSONDecodeError as e:
        print("خطای JSON:", e)
        data = {}  # مقدار پیش‌فرض

async def get_reports(phone):

    users = User.select(User.coldrooms_phone).where(
        (User.telephone.contains(phone))
    )
    # caching = CachedValue()
    # print(caching.get_value())

    # xxx = User.get(User.telephone == phone)
    # print(xxx)
    coldrooms_phone_list=[]
    for user in users:
        PhonCool = user.coldrooms_phone
        #send_message(PhonCool)
        PhonCool = PhonCool.lstrip("0")
        coldrooms_phone_list.append(PhonCool)

    try:
        await asyncio.wait_for(
            get_messages_loop(coldrooms_phone_list),
            timeout = 10
        )
    except asyncio.TimeoutError:
        print("false")
        return False


def index_messages(): # تعداد پیام های خوانده نشده
    data = {'isRead': True}
    response = requests.post('https://console.melipayamak.com/api/receive/inboxcount/162e19ebd29b48b0a87f76b0cd485f9f',
                             json=data)
    index = response.json()
    print('index = ', index['count'], type(index['count']))
    index = index['count']

async def get_messages_loop(coldrooms_phone_list):
    now = CachedValue()
    reports = {}
    while True:
        await get_messages(now, coldrooms_phone_list, reports)
        print(reports)
        if len(reports) >= len(coldrooms_phone_list):
            return False

    print(coldrooms_phone_list)
async def get_messages(now, coldrooms_phone_list, reports): # گزارش پیام های امروز (از ساعت 2 صبح به بعد)
    data = {'type': 'in', 'number': PHONE_MELIPAYAMAK, 'index': 0, 'count': 4}
    response = requests.post('https://console.melipayamak.com/api/receive/messages/162e19ebd29b48b0a87f76b0cd485f9f',
                             json=data)
    data = json.loads(response.text)

    for item in data["messages"]:
        datetime_object = datetime.strptime(item['sendDate'], "%Y-%m-%dT%H:%M:%S.%f")
        if datetime_object > now.get_value() and item['sender'] in coldrooms_phone_list:
            reports[item['sender']] = item["body"]
