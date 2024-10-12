from rest_framework import serializers
# from rest_framework.mixins import RetrieveModelMixin,ListModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from apps.repository import models
from utils.ext.auth import JwtAuthentication
from utils.ext.mixins import ListModelMixin, RetrieveModelMixin
from utils.ext.filter import MineFilterBackend


class UserInfoSerializer(serializers.ModelSerializer):
    mobile = serializers.SerializerMethodField()
    ctime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = models.Company
        fields = ['id', 'username', 'email', 'mobile', 'ctime', 'auth_type']
    def get_mobile(self, obj):
        return obj.mobile[0:3] + "****" + obj.mobile[-4:]


# class UserInfoView(GenericViewSet):
#     def retrieve(self, request):
#         return Response({'code': 200, 'msg': 'hahah'})
class UserInfoView(RetrieveModelMixin, GenericViewSet):
    authentication_classes = [JwtAuthentication, ]
    filter_backends = [MineFilterBackend]
    queryset = models.Company.objects.all()
    serializer_class = UserInfoSerializer

# class UserInfoView(RetrieveModelMixin, GenericViewSet):
#     authentication_classes = [JwtAuthentication, ]
#     queryset = models.Company.objects.all()
#     serializer_class = UserInfoSerializer

# def get(self, request):
# print(request.user["username"])
# print(request.auth)
# instance = models.Company.objects.filter(username=request.user["username"]).first()
# print(instance.auth_type)
# print(type(instance.auth_type))
# # for i in instance:
# #     print(i)
# return Response(
#     {"code": 0, "message": "成功",
#      "data": {"id": instance.id, "username": instance.username, "email": instance.email,
#               "mobile": instance.mobile, "register_time": instance.ctime, "roles": ["admin"],
#               "type": instance.auth_type}})
