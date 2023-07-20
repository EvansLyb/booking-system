

import requests


"""
https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/qrcode-link/url-scheme/generateScheme.html
"""
def generate_scheme(order_id: str):
    request_url = "http://api.weixin.qq.com/wxa/generatescheme"
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {
        "jump_wxa": {
            "path": "/pages/orderDetails/index",
            "query": "id={}".format(order_id),
            "env_version": "release"
        },
        "is_expire": True,
        "expire_type": 1,
        "expire_interval": 1
    }
    try:
      resp = requests.post(request_url, json=data, headers=headers)
      resp = resp.json()

      errcode = resp.get('errcode', None)
      if errcode != 0:
          print("Failed: generate_scheme")
          print(resp.get("errmsg", ""))
          raise Exception(resp.get("errmsg", ""))
      return resp
    except Exception as e:
        print("Failed: generate_scheme")
        print(e)
        raise e
