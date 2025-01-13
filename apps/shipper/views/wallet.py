from django.shortcuts import HttpResponse, redirect
from django.conf import settings

from rest_framework.viewsets import GenericViewSet
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.alipay.AliPay import AliPay
from utils.ext.mixins import ListRetrieveModelMixin
from utils.ext.auth import JwtAuthentication, JwtParamAuthentication, DenyAuthentication
from utils.encrypt import gen_random_oid
from urllib.parse import parse_qs

from apps.repository import models

import requests
from decimal import Decimal


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


class WithDrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(required=True, max_digits=8, decimal_places=2, coerce_to_string=True)
    ali_account = serializers.CharField(required=True)


class WalletView(ListRetrieveModelMixin, GenericViewSet):
    authentication_classes = [JwtAuthentication, JwtParamAuthentication, DenyAuthentication]
    queryset = models.Company.objects.all()
    serializer_class = WalletViewSerializers

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        # print(self.request.user)
        user_id = self.request.user["user_id"]
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

    @action(detail=False, methods=['post'], url_path='withdraw')
    def withdraw(self, request):
        # 执行提现逻辑
        # 1.获取用户提交的数据，表单的校验
        ser = WithDrawSerializer(data=request.data)
        if not ser.is_valid():
            key = list(ser.errors.keys())[0]
            return Response({"code": -1, 'message': ser.errors[key][0]})
        amount = ser.data['amount']
        ali_account = ser.data['ali_account']
        # 2.可用余额 > 提现
        user_id = request.user['user_id']
        company_object = models.Company.objects.filter(id=user_id).first()
        amount = Decimal(amount)
        print("账号", ali_account)
        if company_object.balance < amount:
            return Response({"code": -1, "message": "余额不足"})
        # 3.创建交易记录
        """        
        tran_id = gen_random_oid()
        models.TransactionRecord.objects.create(
            company=company_object,
            tran_type=-1,
            amount=amount,
            ali_account=ali_amount,
            trans_id=tran_id,
            pay_status=0,
            auditor_status=0
        )
        # 4.减少账户余额
        company_object.balance -= amount
        company_object.freeze_balance += amount
        company_object.save()
        """
        tran_id = gen_random_oid()
        models.TransactionRecord.objects.create(
            company=company_object,
            tran_type=-1,
            amount=amount,
            ali_account=ali_account,
            trans_id=tran_id,
            pay_status=1,
        )
        # 4.减少账户余额
        company_object.balance -= amount
        company_object.save()

        # 5.实现转账
        ali_pay = AliPay(
            appid=settings.ALI_APPID,
            app_notify_url=settings.ALI_NOTIFY_URL,
            return_url=settings.ALI_RETURN_URL,
            app_private_key_path=settings.ALI_APP_PRI_KEY_PATH,
            alipay_public_key_path=settings.ALI_PUB_KEY_PATH
        )
        query_params = ali_pay.transfer(
            out_biz_no=tran_id,
            trans_amount=float(amount),
            identity=ali_account,
            order_title="支付宝提现"
        )
        pay_url = "{}?{}".format(settings.ALI_GATEWAY, query_params)
        res = requests.get(pay_url)
        data_dict = res.json()
        print("字典", data_dict)
        if data_dict['alipay_fund_trans_uni_transfer_response']['code'] == '10000':
            return Response({'code': 0, "message": "提现成功", "data": "sdddd"})
        else:
            return Response({"code": -1, "message": "提现失败"})


class ChargeNotifyView(APIView):
    authentication_classes = []

    def get(self, request):
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
        sign = params.pop("sign", None)
        # 2. 签名校验
        # print("params",params)
        # print(request.GET)
        status = ali_pay.verify(params, sign)
        # print("status",status)
        if status:
            # 状态
            out_trade_no = params['out_trade_no']
            # 订单状态修改
            tran_object = models.TransactionRecord.objects.filter(trans_id=out_trade_no, pay_status=0).first()
            # 订单状态更新
            tran_object.pay_status = 1
            tran_object.save()
            # 更新账余额
            tran_object.company.balance += tran_object.amount
            tran_object.company.save()
            return redirect("http://localhost:3333/#/users/wallet?pay=success")
        return redirect("http://localhost:3333/#/users/wallet?pay=error")

    def post(self, request):
        # 异步通知
        ali_pay = AliPay(
            appid=settings.ALI_APPID,
            app_notify_url=settings.ALI_NOTIFY_URL,
            return_url=settings.ALI_RETURN_URL,
            app_private_key_path=settings.ALI_APP_PRI_KEY_PATH,
            alipay_public_key_path=settings.ALI_PUB_KEY_PATH
        )
        # 1. 获取支付宝携带的参数
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)
        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]
        sign = post_dict.pop("sign", None)
        status = ali_pay.verify(post_dict, sign)
        if status:
            out_trade_no = post_dict["out_trade_no"]
            # 3.状态=待支付=>已支付
            return HttpResponse('success')
        return HttpResponse('error')


# from rest_framework.mixins import ListModelMixin,RetrieveModelMixin
# from rest_framework.viewsets import ModelViewSet

from utils.ext.mixins import ListPageNumberModelMixin
from utils.ext.filter import MineBaseFilter
from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import PageNumberPagination


class MinrFilter(MineBaseFilter):
    MINE_FILED = 'company_id'


class TranSearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        tran_type = request.query_params.get('tran_type')
        if tran_type:
            if tran_type == "0":
                queryset = queryset.filter()
            else:
                queryset = queryset.filter(tran_type=tran_type)
        trans_id = request.query_params.get('trans_id')
        if trans_id:
            queryset = queryset.filter(trans_id__contains=trans_id)
        date_range = request.query_params.get('date_range')
        date_range_end = request.query_params.get('date_range_end')
        if date_range and date_range_end:
            queryset = queryset.filter(create_datetime__gte=date_range, create_datetime__lte=date_range_end)

        return queryset


class TranModeSerializer(serializers.ModelSerializer):
    create_datetime = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = models.TransactionRecord
        fields = '__all__'


class TranView(ListPageNumberModelMixin, GenericViewSet):
    authentication_classes = [JwtAuthentication, JwtParamAuthentication, DenyAuthentication]
    filter_backends = [MinrFilter, TranSearchFilter]
    queryset = models.TransactionRecord.objects.all().order_by('-id')
    serializer_class = TranModeSerializer
    pagination_class = PageNumberPagination
