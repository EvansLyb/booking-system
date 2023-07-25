import datetime

from apps.dashboard.models import Order, Bill, BillType, Freeze
from utils import util


def calc_unpay_amount(order_id, order = None, bills = None):
    if not order:
        order = Order.objects.filter(id=order_id).first()
    if not bills:
        bills = Bill.objects.filter(order_id=order_id)

    order_price = order.price
    """ === calculate accumulative total amount === """
    accumulative_total_amount = 0
    for bill in bills:
        if bill.bill_type == BillType.PAYMENT:
            accumulative_total_amount += bill.amount
        elif bill.bill_type == BillType.REFUND:
            accumulative_total_amount -= bill.amount

    checkout_price = order_price - accumulative_total_amount
    return checkout_price


def unfreeze(facility_id, date, time_list, court_type):
    for time_str in time_list:
        time_obj = datetime.datetime.strptime(time_str, '%H:%M')
        freeze = Freeze.objects.filter(facility_id=facility_id, date=date, time=datetime.time(hour=time_obj.hour, minute=time_obj.minute)).first()
        if not freeze:
            return
        new_freeze_weights = freeze.weights - util.get_freeze_weights_by_court_type(court_type)
        freeze.is_order = True if new_freeze_weights > 0 else False
        freeze.weights = new_freeze_weights
        freeze.save()


def freeze(facility_id, date, time_list, court_type):
    for time_str in time_list:
        time_obj = datetime.datetime.strptime(time_str, '%H:%M')
        freeze = Freeze.objects.filter(facility_id=facility_id, date=date, time=datetime.time(hour=time_obj.hour, minute=time_obj.minute)).first()
        if freeze:
            freeze.is_order = True
            freeze.weights = freeze.weights + util.get_freeze_weights_by_court_type(court_type)
        else:
            freeze = Freeze(
                facility_id=facility_id,
                date=date,
                time=datetime.time(hour=time_obj.hour, minute=time_obj.minute),
                is_order=True,
                weights=util.get_freeze_weights_by_court_type(court_type)
            )
        freeze.save()


def check_if_order_is_cancellable(order_id) -> bool:
    bill_list = Bill.objects.filter(order_id=order_id)
    if not bill_list:
        return True
    return False
