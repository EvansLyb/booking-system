from django.conf import settings

import requests


"""
https://developers.weixin.qq.com/minigame/dev/wxcloudrun/src/development/storage/service/upload.html
"""
def get_upload_file_info(path: str):
    request_url = "http://api.weixin.qq.com/tcb/uploadfile"
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {
        "env": settings.CLOUD_ENV,
        "path": path
    }
    try:
      resp = requests.post(request_url, json=data, headers=headers)
      resp = resp.json()

      errcode = resp.get('errcode', None)
      if errcode != 0:
          raise Exception(resp.get("errmsg", ""))
      return resp
    except Exception as e:
       print(e)
       raise e


"""
https://developers.weixin.qq.com/minigame/dev/wxcloudrun/src/development/storage/service/upload.html
"""
def upload_file(url, request_path, authorization, token, file_id, file):
    form = {
        "key": request_path,
        "Signature": authorization,
        "x-cos-security-token": token,
        "x-cos-meta-fileid": file_id,
        "file": file
    }
    try:
        resp = requests.post(url=url, files=form)
        return resp
    except Exception as e:
        print(e)
        raise e


"""
https://developers.weixin.qq.com/minigame/dev/wxcloudrun/src/development/storage/service/download.html
"""
def get_download_url_by_file_id(file_id):
    request_url = "http://api.weixin.qq.com/tcb/batchdownloadfile"
    data = {
        "env": settings.CLOUD_ENV,
        "file_list": [
          {
              "fileid": file_id,
              "max_age": 86400
          }
        ]
    }
    try:
      resp = requests.post(request_url, json=data)
      resp = resp.json()

      errcode = resp.get('errcode', None)
      if errcode != 0:
          raise Exception(resp.get("errmsg", ""))
      return resp.get("file_list", [])[0].get("download_url", "")
    except Exception as e:
       raise e


def get_image_url_by_fiel_path(file_path):
   return "{}/{}".format(
      settings.OSS_DOMAIN,
      file_path
   )
