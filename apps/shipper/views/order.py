from rest_framework import serializers
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination

from utils.ext.auth import JwtAuthentication, JwtParamAuthentication, DenyAuthentication
from rest_framework.response import Response
from utils.ext.mixins import CreateModelMixin, ListPageNumberModelMixin
# from rest_framework.mixins import CreateModelMixin
from apps.repository import models

import random
import datetime


class OrderPageNumberPagination(PageNumberPagination):
    page_size = 30


class OrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        # fields = '__all__'
        exclude = ["company", "driver"]

        extra_kwargs = {
            "unit_price": {"coerce_to_string": False},
            "weight": {"coerce_to_string": False},
            "oid": {"read_only": True}
        }


class OrderView(CreateModelMixin, ListPageNumberModelMixin, GenericViewSet):
    authentication_classes = [JwtAuthentication, JwtParamAuthentication, DenyAuthentication]
    serializer_class = OrderModelSerializer
    queryset = models.Order.objects.all()
    pagination_class = OrderPageNumberPagination

    def perform_create(self, serializer):
        # 1.company_id
        company_id = self.request.user["user_id"]
        # 2.检查余额
        instance = models.Company.objects.filter(id=company_id).first()
        total_amount = serializer.validated_data["unit_price"] * serializer.validated_data["weight"]
        if instance.balance < total_amount:
            return Response({"code": -1, "message": "余额不足"})

        # 3.订单号
        oid = self.order_number()
        # 4.创建订单
        serializer.save(company_id=company_id, oid=oid)
        # 5.交易记录
        trans_id = self.order_number()
        models.TransactionRecord.objects.create(
            tran_type=2,
            trans_id=trans_id,
            order_id=oid,
            company_id=company_id,
            amount=total_amount,
            pay_status=1
        )

        # 6.可用 -> 不可用
        instance.balance -= total_amount
        instance.freeze_balance += total_amount
        instance.save()

    def order_number(self):
        random_number = random.randint(100000000, 999999999)
        ctime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        return "{}{}".format(ctime, random_number)
