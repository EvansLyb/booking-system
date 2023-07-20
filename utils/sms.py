from django.conf import settings
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile


"""
--- send to admin ---
Scene 1: use created a new order

--- send to user ---
Scene 1: order price up && order status != Rejected
Scene 2: order status changed to Accepted
Scene 2: order status changed to Rejected
"""

""" https://cloud.tencent.com/document/product/382/43196 """
def send_sms(phone_number_list, template_id, template_param_list):
    if not phone_number_list or len(phone_number_list) == 0:
        return

    cred = credential.Credential(settings.TENCENT_CLOUD_SECRET_ID, settings.TENCENT_CLOUD_SECRET_KEY)

    httpProfile = HttpProfile()

    clientProfile = ClientProfile()
    clientProfile.signMethod = "TC3-HMAC-SHA256"
    clientProfile.language = "en-US"
    clientProfile.httpProfile = httpProfile

    client = sms_client.SmsClient(cred, "ap-guangzhou", clientProfile)

    req = models.SendSmsRequest()
    req.SmsSdkAppId = settings.TENCENT_CLOUD_SMS_SDK_APP_ID
    req.SignName = settings.TENCENT_CLOUD_SMS_SIGN_NAME
    req.TemplateId = template_id
    req.TemplateParamSet = template_param_list
    req.PhoneNumberSet = phone_number_list
    try:
      resp = client.SendSms(req)
      print('request sendsms, resp:')
      print(resp)
      return resp
    except Exception as e:
        print("Failed: send_sms")
        print(e)
        raise e
