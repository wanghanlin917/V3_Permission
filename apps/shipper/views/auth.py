from rest_framework.viewsets import GenericViewSet
from utils.ext.mixins import RetrieveModelMixin,UpdateModelMixin
class AuthView(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    pass
