from django.conf import settings

import requests



""" https://developers.weixin.qq.com/miniprogram/dev/wxcloudrun/src/scene/deploy/subscribe.html """
""" https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/mp-message-management/subscribe-message/sendMessage.html """
def send_subscribe_message_after_order_status_update(open_id, order_no, order_status, facility_name, order_id):
    request_url = "http://api.weixin.qq.com/cgi-bin/message/subscribe/send"
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {
        "touser": open_id,
        "template_id": settings.TENCENT_CLOUD_SUBSCRIBE_MESSAGE_ID_ORDER_STATUS_UPDATED,
        "miniprogram_state": "formal",
        "data": {
            "character_string1": {
                "value": order_no
            },
            "thing2": {
                "value": order_status
            },
            "thing17": {
                "value": facility_name[:16] + ".."  # 20 characters limit
            }
        },
        "page": "pages/orderDetails/index?id={}".format(order_id)
    }
    try:
      print("Request: /cgi-bin/message/subscribe/send, data: ")
      print(data)
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
