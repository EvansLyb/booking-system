from apps.dashboard.models import CourtType

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
