from rest_framework.viewsets import GenericViewSet
from rest_framework import serializers
from utils.ext.mixins import ListRetrieveModelMixin
from utils.ext.auth import JwtAuthentication, JwtParamAuthentication, DenyAuthentication
from apps.repository import models


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
