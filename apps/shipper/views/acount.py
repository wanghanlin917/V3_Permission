from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.repository import models
from utils.jwt_auth import create_token
from utils.SendSms import SendSMS

from apps.shipper.serializers.acount import LoginSerializer, LoginSmsSerializer, RegisterSerializer, SendSmsSerializer


class LoginView(APIView):
    def post(self, request):
        # print(request.data)
        # 1.数据格式校验
        ser = LoginSerializer(data=request.data)
        # ser.is_valid(raise_exception=True)
        # print(ser.initial_data)
        if not ser.is_valid():
            print(ser.errors)
            return Response({"code": -1, "message": "登录失败"})
        # 2.数据库合法性校验 print(ser.data)
        # print("login",ser.data)
        instance = models.Company.objects.filter(**ser.data).first()
        # 2.1登录失败
        if not instance:
            return Response({"code": -2, "message": "用户名或密码错误"})
        token = create_token({'user_id': instance.id, 'username': instance.username})
        # print(token)
        # 2.2登录成功
        return Response(
            {"code": 0, "message": "成功", "data": {"token": token, "username": instance.username, "id": instance.id}})


class SendSmsView(APIView):
    def post(self, request):
        try:
            ser = SendSmsSerializer(data=request.data)
            # print(ser.initial_data)
            # print("ser", ser.is_valid())
            if not ser.is_valid():
                # print(ser.errors)
                # print("jdjdfj",ser.errors["mobile"])
                # err = [key for key, value in ser.errors.items()]
                key = list(ser.errors.keys())[0]
                return Response({"code": -1, "message": ser.errors[key][0]})
            # print(type(ser.data))
            # 短信发送接口
            import random
            random_code = random.randint(1000, 9999)
            SendSMS(ser.data["mobile"], random_code)
            # 保存到redis（启动redis服务、配置redis链接、请求保存）
            from django_redis import get_redis_connection
            conn = get_redis_connection("default")
            conn.set(ser.validated_data["mobile"], random_code, ex=60)
            return Response({"code": 0, "message": "发送成功", "data": ser.data})
        except Exception as e:
            print("错误", e)
            return Response({"code": -1, "message": e})


class SmsLoginView(APIView):
    def post(self, request):
        # print(request.data)
        try:
            ser = LoginSmsSerializer(data=request.data)
            if not ser.is_valid():
                # print(ser.errors)
                key = list(ser.errors.keys())[0]
                return Response({"code": -1, "message": ser.errors[key][0]})
            # print(ser.validated_data)
            # 校验成功
            instance = models.Company.objects.filter(mobile=ser.validated_data["mobile"]).first()
            token = create_token({'user_id': instance.id, 'username': instance.username})
            return Response({
                "code": 0,
                "message": "成功",
                "data": {"token": token, "username": instance.username}
            })
        except Exception as e:
            print("--->", e)
            return Response({"code": -1, "message": "发送失败"})


class RegisterView(APIView):
    def post(self, request):
        try:
            print(request.data)
            ser = RegisterSerializer(data=request.data)
            print(ser.is_valid())
            if not ser.is_valid():
                key = list(ser.errors.keys())[0]
                return Response({"code": -1, "message": ser.errors[key][0]})
            ser.validated_data.pop("code")
            ser.validated_data.pop("confirmPassword")
            ser.save()
            # print(ser.validated_data)
            instance = models.Company.objects.filter(**ser.validated_data).first()
            return Response({"code": 0, "message": "成功",
                             "data": {"username": instance.username, "mobile": instance.mobile,
                                      "email": instance.email}})
        except Exception as e:
            return Response({"code": -1, "message": e})
