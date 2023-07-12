from apps.dashboard.models import Order, Bill, BillType


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
