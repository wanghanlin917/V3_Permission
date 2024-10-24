from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from utils.ext.mixins import RetrieveModelMixin, UpdateModelMixin
from utils.ext.auth import JwtAuthentication,JwtParamAuthentication,DenyAuthentication
from apps.repository import models


class AuthModelSerializers(serializers.ModelSerializer):
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

    def get_auth_type_class(self, obj):
        return models.Company.auth_type_class_map[obj.company.auth_type]

    def get_licence_path_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.licence_path)

    def get_legal_identity_front_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.legal_identity_front_url)

    def get_legal_identity_back_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.legal_identity_back_url)


class AuthView(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    authentication_classes = [JwtAuthentication,JwtParamAuthentication,DenyAuthentication]
    queryset = models.CompanyAuth.objects.all()
    serializer_class = AuthModelSerializers

    @action(detail=False, methods=['post'],url_path="upload")
    def upload(self,request):
        upload_obj = request.FILES('file')
        print(upload_obj.name)
        return Response({"code":0,"message":"success"})

