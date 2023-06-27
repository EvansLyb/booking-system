from django.conf import settings

import requests

def send_sms():
    request_url = "http://api.weixin.qq.com/tcb/sendsms"
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {
        "env": settings.CLOUD_ENV,
        "sms_type": "Notification",
        "template_id": "923584",
        "template_param_list": ["商品", "/index.html"],
        "phone_number_list": ["+8613751787141"],
        "use_short_name": False,
        "resource_appid": settings.APP_ID
    }
    try:
      resp = requests.post(request_url, json=data, headers=headers)
      resp = resp.json()
      print('request sendsmsv2, resp:')
      print(resp)

      errcode = resp.get('errcode', None)
      if errcode != 0:
          print("Failed: send_sms")
          print(resp.get("errmsg", ""))
          raise Exception(resp.get("errmsg", ""))
      return resp
    except Exception as e:
        print("Failed: send_sms")
        print(e)
        raise e
