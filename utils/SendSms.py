from unisdk.sms import UniSMS
from unisdk.exception import UniException

# 初始化
client = UniSMS("n2BNbBdnABrQuPaHAK4bdFeGtAykzWQ86JXVGBft2SeNXc1zK",
                "XN12G8j9RSkjgQgDGjuw1HdRAaF5JG")  # 若使用简易验签模式仅传入第一个参数即可
def SendSMS(mobile,code):
    try:
        # 发送短信
        res = client.send({
            "to": mobile,
            "signature": "小王学python",
            "templateId": "pub_verif_ttl",
            "templateData": {
                "code": code,
                "ttl": 1
            }
        })
        # print(res.data)
    except UniException as e:
        print(e)

