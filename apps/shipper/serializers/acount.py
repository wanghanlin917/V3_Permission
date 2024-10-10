from rest_framework import serializers
from rest_framework import exceptions
from django.core.validators import RegexValidator
from django_redis import get_redis_connection

from utils.encrypt import md5
from apps.repository import models


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_password(self, value):
        return md5(value)


class SendSmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=True, validators=[RegexValidator(r"\d{11}", message="格式错误")])

    # username = serializers.CharField(required=False)

    def validate_mobile(self, value):
        exists = models.Company.objects.filter(mobile=value).exists()
        # print(self.initial_data)
        # print(type(self.initial_data))
        # print(username)
        # print("username" in self.initial_data.keys())
        if not exists:
            if "username" in self.initial_data.keys():
                return value
            else:
                raise exceptions.ValidationError("手机号不存在")
        return value


class LoginSmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=True, validators=[RegexValidator(r"\d{11}", message="格式错误")])
    code = serializers.CharField(required=True, validators=[RegexValidator(r"\d{4}", message="格式错误")])

    def validate_mobile(self, value):
        exists = models.Company.objects.filter(mobile=value).exists()
        if not exists:
            raise exceptions.ValidationError("手机未注册")
        return value

    def validate_code(self, value):
        # 去redis中获取
        # self.validated_data
        # self.initial_data
        mobile = self.initial_data.get('mobile')
        # 在redis中校验
        conn = get_redis_connection('default')
        cache_code = conn.get(mobile)
        if not cache_code:
            raise exceptions.ValidationError("验证码不存在或已过期")
        cache_code = cache_code.decode("utf-8")
        if cache_code != value:
            raise exceptions.ValidationError("验证码错误")
        conn.delete(mobile)
        return value


class RegisterSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(required=True, validators=[RegexValidator(r"\d{11}", message="格式错误")])
    code = serializers.CharField(required=True, validators=[RegexValidator(r"\d{4}", message="格式错误")])
    confirmPassword = serializers.CharField(required=True)

    class Meta:
        model = models.Company
        fields = ['username', 'mobile', 'email', 'code', 'password', 'confirmPassword']

    def validate_mobile(self, value):
        exists = models.Company.objects.filter(mobile=value).exists()
        if exists:
            raise exceptions.ValidationError("手机号已注册")
        return value

    def validate_password(self, value):
        return md5(value)

    def validate_confirm_password(self, value):
        password = self.initial_data.get('password')
        if value != password:
            raise exceptions.ValidationError("密码不一致")
        return value

    def validate_code(self, value):
        mobile = self.initial_data.get('mobile')
        conn = get_redis_connection('default')
        cache_code = conn.get(mobile)
        if not cache_code:
            raise exceptions.ValidationError("验证码不存在或已过期")
        cache_code = cache_code.decode("utf-8")
        if cache_code != value:
            raise exceptions.ValidationError("验证码错误")
        conn.delete(mobile)
        return value
