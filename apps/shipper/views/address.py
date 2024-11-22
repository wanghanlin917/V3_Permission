from utils.ext.mixins import ListRetrieveModelMixin
from rest_framework.viewsets import GenericViewSet


class AddressView(ListRetrieveModelMixin, GenericViewSet):
    pass
