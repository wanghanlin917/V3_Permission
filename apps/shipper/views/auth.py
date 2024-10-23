from rest_framework import serializers
from rest_framework.viewsets import GenericViewSet
from utils.ext.mixins import RetrieveModelMixin, UpdateModelMixin
from apps.repository import models


class AuthModelSerializer(serializers.ModelSerializer):
    # auth_type_text = serializers.CharField(source="company.auth_type_text",read_only=True)
    auth_type_class = serializers.SerializerMethodField(read_only=True)
    licence_path_url = serializers.SerializerMethodField()
    legal_identity_front_url = serializers.SerializerMethodField()
    legal_identity_back_url = serializers.SerializerMethodField()
    class Meta:
        model = models.CompanyAuth
        exclude = ["company"]
        extra_kwargs = {
            'remark': {"read_only": True}
        }
    def get_auth_type_class(self,obj):
        return models.Company.auth_type_class_map[obj.company.auth_type]
    

class AuthView(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):


