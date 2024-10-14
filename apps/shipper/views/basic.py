from django.core.validators import RegexValidator
from rest_framework import serializers
# from rest_framework.mixins import ListModelMixin,UpdateModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import exceptions
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from apps.repository import models
from utils.ext.auth import JwtAuthentication
from utils.ext.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from utils.ext.filter import MineFilterBackend


class UserInfoSerializer(serializers.ModelSerializer):
    mobile = serializers.SerializerMethodField()
    ctime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = models.Company
        fields = ['id', 'username', 'email', 'mobile', 'ctime', 'auth_type']

    def get_mobile(self, obj):
        return obj.mobile[0:3] + "****" + obj.mobile[-4:]


class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ['username']


class MobileSerializer(serializers.ModelSerializer):
    old_mobile = serializers.CharField(write_only=True)
    # source可以解决前后端的字段不通
    new_mobile = serializers.CharField(write_only=True, source="mobile",
                                       validators=[RegexValidator(r'\d{11}', message="手机格式错误")])
    t_mobile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Company
        fields = ['old_mobile', 't_mobile', 'mobile', 'new_mobile']
        extra_kwargs = {
            'old_mobile': {'validators': [RegexValidator(r'\d{11}', message="手机格式错误")]},
        }

    def validate_old_mobile(self, value):
        request = self.context['request']
        user_id = request.user["user_id"]
        exits = models.Company.objects.filter(id=user_id, mobile=value).exists()
        if not exits:
            raise exceptions.ValidationError("原手机号错误")
        return value

    def get_t_mobile(self, value):
        return value.mobile[0:3] + "****" + value.mobile[-4:]


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = ['email']


class UserInfoView(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    authentication_classes = [JwtAuthentication, ]
    filter_backends = [MineFilterBackend]
    queryset = models.Company.objects.all()
    serializer_class = UserInfoSerializer

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            req_type = self.request.query_params.get('type')
            if req_type == 'username':
                return NameSerializer
            elif req_type == 'mobile':
                return MobileSerializer
            elif req_type == 'email':
                return EmailSerializer
        return UserInfoSerializer
