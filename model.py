import re
from datetime import datetime
from peewee import MySQLDatabase, Model, CharField, IntegerField, Insert
from playhouse.db_url import connect


database = connect('mysql://voip:1234@127.0.0.1:3306/voip')


class BaseModel(Model):
    class Meta:
        database = database

    def __str__(self):
        return str(self.id)


class User(BaseModel):
    id = None
    telephone = CharField(max_length=11)
    name = CharField(max_length=255)
    coldrooms_number = CharField(max_length=255)
    coldrooms_phone = CharField(max_length=255)


def validate_phone(value):
    pattern = r"^(?:\+98|0098|98|0)?(9\d{9})$"
    match = re.match(pattern, value)

    if match:
        # گرفتن شماره اصلی (10 رقمی که با 9 شروع می‌شود)
        main_number = match.group(1)
        # افزودن پیشوند 0 به شماره
        return f"0{main_number}"
    else:
        # شماره نامعتبر است
        return False

class CachedValue:
    def __init__(self):
        self.cached_value = None

    def get_value(self):
        if self.cached_value is None:  # مقداردهی تنها در بار اول
            self.cached_value = datetime.now()
        return self.cached_value

    def reset_value(self):  # بازنشانی مقدار
        self.cached_value = datetime.now()
