# app/utils/date_utils.py

import jdatetime
from datetime import timedelta
from config import INVOICE_VALIDITY_DAYS

def get_shamsi_date():
    """
    Returns today's date in Shamsi (Jalali) format: YYYY/MM/DD
    """
    now = jdatetime.datetime.now()
    return now.strftime("%Y/%m/%d")

def get_future_shamsi_date(days=INVOICE_VALIDITY_DAYS):
    """
    Returns a future date in Shamsi (Jalali) format: YYYY/MM/DD
    Default is 30 days from now
    """
    now = jdatetime.datetime.now()
    future_date = now + timedelta(days=days)
    return future_date.strftime("%Y/%m/%d")