from rest_framework.viewsets import GenericViewSet
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.alipay.AliPay import AliPay
from utils.ext.mixins import ListRetrieveModelMixin
from utils.ext.auth import JwtAuthentication, JwtParamAuthentication, DenyAuthentication
from utils.encrypt import gen_random_oid

from apps.repository import models

from django.conf import settings


class WalletViewSerializers(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    # balance = serializers.DecimalField(coerce_to_string=False, max_digits=10, decimal_places=2)
    class Meta:
        model = models.Company
        fields = ["total", "balance", "freeze_balance"]
        extra_kwargs = {
            "balance": {"coerce_to_string": False},
            "freeze_balance": {"coerce_to_string": False}
        }

    def get_total(self, obj):
        return obj.balance + obj.freeze_balance


class WalletView(ListRetrieveModelMixin, GenericViewSet):
    authentication_classes = [JwtAuthentication, JwtParamAuthentication, DenyAuthentication]
    queryset = models.Company.objects.all()
    serializer_class = WalletViewSerializers

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        # print(self.request.user)
        user_id = self.request.user["user_id"]
        print(user_id)
        return queryset.filter(id=user_id).first()

    @action(detail=False, methods=["post"], url_path="charge")
    def charge(self, request):
        # 序列化校验
        user_id = request.user["user_id"]
        out_trade_no = gen_random_oid()

        # 生成交易记录
        models.TransactionRecord.objects.create(
            company_id=user_id,
            tran_type=1,
            amount=request.data["amount"],
            trans_id=out_trade_no,
            pay_status=0
        )
        ali_pay = AliPay(
            appid=settings.ALI_APPID,
            app_notify_url=settings.ALI_NOTIFY_URL,
            return_url=settings.ALI_RETURN_URL,
            app_private_key_path=settings.ALI_APP_PRI_KEY_PATH,
            alipay_public_key_path=settings.ALI_PUB_KEY_PATH
        )

        query_params = ali_pay.direct_pay(
            subject="平台充值",  # 商品简单描述
            out_trade_no=out_trade_no,  # 商户订单号
            total_amount=request.data['amount']
        )
        pay_url = "{}?{}".format(settings.ALI_GATEWAY, query_params)
        return Response({"code": 0, "message": "success", "data": pay_url})


class ChargeNotifyView(APIView):
    authentication_classes = []
    def get(self,request):
        # 支付成功后页面会跳转到这里
        ali_pay = AliPay(
            appid=settings.ALI_APPID,
            app_notify_url=settings.ALI_NOTIFY_URL,
            return_url=settings.ALI_RETURN_URL,
            app_private_key_path=settings.ALI_APP_PRI_KEY_PATH,
            alipay_public_key_path=settings.ALI_PUB_KEY_PATH
        )
        # 1. 获取支付宝携带的参数
        params = request.GET.dict()
        sign = params.pop("sign",None)
        # 2. 签名校验
        print("params",params)
        print(request.GET)
        status = ali_pay.verify(params, sign)
        print("status",status)
