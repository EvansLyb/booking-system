from django.conf import settings

import requests


def unified_order(open_id, out_trade_no, total_price):
    request_url = "http://api.weixin.qq.com/_/pay/unifiedorder"
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {
        "body": "payment",
        "openid": open_id,
        "out_trade_no": out_trade_no,
        "spbill_create_ip": "127.0.0.1",
        "env_id": settings.CLOUD_ENV,
        "sub_mch_id": settings.MCH_ID,
        "total_fee": total_price * 100,
        "callback_type": 2,
        "container": {
           "service": settings.SERVICE,
           "path": "/apis/pay/callback"
        }
    }
    try:
      resp = requests.post(request_url, json=data, headers=headers)
      print('---')
      print('debug')
      print(resp)
      resp = resp.json()
      print('json')
      print(resp)

      errcode = resp.get('errcode', None)
      if errcode != 0:
          print("Failed: unified_order")
          print(resp.get("errmsg", ""))
          raise Exception(resp.get("errmsg", ""))
      return resp
    except Exception as e:
        print("Failed: unified_order")
        print(e)
        raise e
