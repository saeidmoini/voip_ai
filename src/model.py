import re
from datetime import datetime
from peewee import Model, CharField, AutoField
from playhouse.db_url import connect
from config import DB_USER, DB_PASS, DB_PORT, DB_DATABASE

database = connect(f'mysql://{DB_USER}:{DB_PASS}@127.0.0.1:{DB_PORT}/{DB_DATABASE}')


class BaseModel(Model):
    class Meta:
        database = database

    def __str__(self):
        return str(self.id)


class User(BaseModel):
    id = AutoField(primary_key=True)
    telephone = CharField(max_length=11)
    name = CharField(max_length=255)
    city = CharField(max_length=255, null=True)
    coldrooms_code = CharField(max_length=255)
    coldrooms_phone = CharField(max_length=255)
    
    
# تعریف کلاس LoginUser برای احراز هویت کاربران
class LoginUser(BaseModel):
    id = AutoField(primary_key=True)
    username = CharField(max_length=80, unique=True)
    password = CharField(max_length=120)
    auth_token = CharField(max_length=120, null=True)  # برای ذخیره توکن احراز هویت
    
    class Meta:
        table_name = 'users'


with database:
    database.create_tables([User])


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



