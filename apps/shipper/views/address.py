from rest_framework import serializers
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination

from apps.repository import models
# from utils.ext.mixins import ListRetrieveModelMixin
from utils.ext.mixins import ListPageNumberModelMixin
from utils.ext.filter import MineBaseFilter

class AddressPageNumberPagination(PageNumberPagination):
    page_size = 20

class MineFilter(MineBaseFilter):
    MINE_FILED = "company_id"

class AddressModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = "__all__"

class AddressView(ListPageNumberModelMixin, GenericViewSet):
    filter_backends = [MineFilter,]
    pagination_class = AddressPageNumberPagination
    serializer_class = AddressModelSerializer
    queryset = models.Address.objects.all().order_by('-id')
