from django.conf import settings

import requests



""" https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/scene/deploy/subscribe.html """
""" https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/subscribe-message/sendMessage.html """
def send_subscribe_message(open_id, order_no, order_status, facility_name):
    request_url = "http://api.weixin.qq.com/cgi-bin/message/subscribe/send"
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {
        "touser": open_id,
        "template_id": settings.TENCENT_CLOUD_SUBSCRIBE_MESSAGE_ID_ORDER_STATUS_UPDATED,
        "miniprogram_state": "developer",
        "data": {
            "character_string1": order_no,
            "thing2": order_status,
            "thing17": facility_name
        }
    }
    try:
      resp = requests.post(request_url, json=data, headers=headers)
      resp = resp.json()

      errcode = resp.get('errcode', None)
      if errcode != 0:
          print("Failed: send_subscribe_message")
          print(resp.get("errmsg", ""))
      return resp
    except Exception as e:
        print("Failed: send_subscribe_message")
        print(e)
        pass
