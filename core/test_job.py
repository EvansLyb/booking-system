import os, sys, time, datetime


UNPAID_ORDER_SURVIVAL_TIME = 15  # Unit: seconds

def automatic_cancellation_of_unpaid_orders():
    while True:
        try:
            now = datetime.datetime.now()
            local_time = now.strftime('%Y-%m-%d %H:%M:%S')
            print('local time：' + str(local_time))
            time.sleep(1)
        except Exception as e:
            print('Error: automatic_cancellation_of_unpaid_orders')
            print(str(e))
            continue


if __name__ == "__main__":
    automatic_cancellation_of_unpaid_orders()
