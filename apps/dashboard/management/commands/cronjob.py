import os, sys, time, datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from apps.dashboard.models import Order, UnpaidOrder, OrderStatus
from utils.order import check_if_order_is_cancellable, unfreeze
from utils.util import trans_list_str_to_list


UNPAID_ORDER_SURVIVAL_TIME = 30 * 60  # Unit: seconds

def automatic_cancellation_of_unpaid_orders():
    while True:
        try:
            local_time = now().strftime('%Y-%m-%d %H:%M:%S')
            print('local time：' + str(local_time))
            unpaid_order_list = UnpaidOrder.objects.all()
            if unpaid_order_list and len(unpaid_order_list) > 0:
                for unpaid_order in unpaid_order_list:
                    order = Order.objects.get(id=unpaid_order.order_id)
                    if order.status != OrderStatus.PENDING_PAYMENT:
                        unpaid_order.delete()
                    else:
                        if (now() - order.created_at).seconds > UNPAID_ORDER_SURVIVAL_TIME:
                            # cancel this order
                            is_cancellable = check_if_order_is_cancellable(order)
                            if is_cancellable:
                                order.status = OrderStatus.CANCELLED
                                order.save()
                                """ === data unfreeze === """
                                unfreeze(order.facility_id, order.date, trans_list_str_to_list(order.time_list), order.court_type)
                            else:
                                errmsg = "order {} is not cancellable".format(order.id)
                                print("Failed: automatic_cancellation_of_unpaid_orders")
                                print(errmsg)
                            unpaid_order.delete()
            time.sleep(1)
        except Exception as e:
            print('Error: automatic_cancellation_of_unpaid_orders')
            print(str(e))
            continue

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            automatic_cancellation_of_unpaid_orders()
        except Exception as e:
            print('Error: cronjob')
            print(str(e))
