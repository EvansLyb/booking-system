from apps.dashboard.models import CourtType

from ast import literal_eval
from decimal import Decimal
import datetime
import random


def get_freeze_weights_by_court_type(court_type: CourtType) -> Decimal:
    mapping = {
        CourtType.FULL: Decimal('1'),
        CourtType.HALF: Decimal('0.5'),
        CourtType.QUARTER: Decimal('0.25')
    }
    return mapping[court_type]


def generate_order_no():
    now = datetime.datetime.now()
    order_no = now.strftime("%y%m%d%H%M") + str(random.randint(1000, 9999))
    return order_no


def generate_trade_no():
    now = datetime.datetime.now()
    trade_no = str(now).replace('.', '').replace('-', '').replace(':', '').replace(' ', '')
    return trade_no


def trans_time_to_slot(time_str):
    from_time_str = time_str
    from_time = datetime.datetime.strptime(time_str, '%H:%M')
    delta = datetime.timedelta(minutes=30)
    to_time = from_time + delta
    to_time_str = datetime.time(hour=to_time.hour, minute=to_time.minute).isoformat(timespec='minutes')
    return "{} - {}".format(from_time_str, to_time_str)


"""
- time_list: ["08:30", "12:00", "19:00"]
- output: ["08:30 - 09:00", "12:00 - 12:30", "19:00 - 19:30"]
"""
def format_order_time_list(time_list):
    return [trans_time_to_slot(time_str) for time_str in literal_eval(time_list)]
