import os, sys, time, datetime
import threading
from django.core.management.base import BaseCommand

from apps.dashboard.models import Order, UnpaidOrder


def automatic_cancellation_of_unpaid_orders():
    while True:
        try:
            loca_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print('local time：'+str(loca_time))
            order = Order.objects.all().first()
            print('test cronjob')
            print(order.id)
            print(order.phone_number)
            print(order.status)
            print(order.date)
            print(order.time_list)
            order.remark = loca_time
            order.save()
            time.sleep(1)
        except Exception as e:
            print('Error: automatic_cancellation_of_unpaid_orders')
            print(str(e))
            continue

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            task1 = threading.Thread(target=automatic_cancellation_of_unpaid_orders)
            task1.start()
        except Exception as e:
            print('Error: cronjob')
            print(str(e))
