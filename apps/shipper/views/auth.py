from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework import viewsets
# from rest_framework.mixins import ListModelMixin, RetrieveModelMixin,CreateModelMixin,UpdateModelMixin,DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from utils.ext.mixins import RetrieveModelMixin, CreateUpdateModelMixin
from utils.ext.auth import JwtAuthentication, JwtParamAuthentication, DenyAuthentication
from apps.repository import models
from datetime import datetime
import os
from django.conf import settings
from django.core.files.storage import default_storage


def get_upload_filename(file_name):
    data_path = datetime.now().strftime('%Y%m%d')
    upload_path = os.path.join(settings.UPLOAD_PATH, data_path)
    file_path = os.path.join(upload_path, file_name)
    return default_storage.get_available_name(file_path)


def baidu_ai(bytes_body):
    import base64
    import requests
    response = requests.get(
        url='https://aip.baidubce.com/oauth/2.0/token',
        params={
            'grant_type': 'client_credentials',
            'client_id': 'rzKM6pAn5lQ0Q7Ono5GDyLxX',
            'client_secret': 'sl1X2owi5Io5pbc6pTTInxQByLLR2d05'
        }
    )
    data_dict = response.json()
    access_token = data_dict['access_token']
    print("token", access_token)
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard"
    img = base64.b64encode(bytes_body)
    params = {"id_card_side": "front", "image": img}
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    res = requests.post(request_url, data=params, headers=headers)
    res_dict = res.json()
    # for k, v in res_dict["words_result"].items():
    #     print(k, v)
    return res_dict["words_result"]


class AuthModelSerializers(serializers.ModelSerializer):
    auth_type = serializers.CharField(source="company.auth_type", read_only=True)
    # auth_type_class = serializers.SerializerMethodField(read_only=True)
    licence_path_url = serializers.SerializerMethodField()
    legal_identity_front_url = serializers.SerializerMethodField()
    legal_identity_back_url = serializers.SerializerMethodField()

    class Meta:
        model = models.CompanyAuth
        exclude = ["company"]
        extra_kwargs = {
            'remark': {"read_only": True}
        }

    # def get_auth_type_class(self, obj):
    #     return models.Company.auth_type_class_map[obj.company.auth_type]

    def get_licence_path_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.licence_path)

    def get_legal_identity_front_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.legal_identity_front)

    def get_legal_identity_back_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.legal_identity_back)


class AuthView(RetrieveModelMixin, CreateUpdateModelMixin, GenericViewSet):
    authentication_classes = [JwtAuthentication, JwtParamAuthentication, DenyAuthentication]
    queryset = models.CompanyAuth.objects.all()
    serializer_class = AuthModelSerializers

    @action(detail=False, methods=['post'], url_path="upload")
    def upload(self, request):
        print(request)
        print(request.FILES.get('file'))
        # upload_obj = request.FILES('file')
        # print(upload_obj.name)
        upload_object = request.FILES.get('file')
        # print("upload_object",upload_object.data)
        if upload_object.size > 10 * 1024 * 1024:
            return Response({
                "code": -1,
                "msg": "文件太大"
            })
        upload_url = get_upload_filename(upload_object.name)
        save_path = default_storage.save(upload_url, upload_object)
        local_url = default_storage.url(save_path)
        abs_url = request.build_absolute_uri(local_url)
        img_type = request.data.get("type")
        if img_type == "front":
            upload_object.seek(0)
            res = baidu_ai(upload_object.read())
            print(res["姓名"]["words"])
            print(res["公民身份号码"]["words"])
            return Response({"code": 0, "message": "success",
                             "data": {"url": local_url, "abs_url": abs_url, "name": res["姓名"]["words"],
                                      "cardId": res["公民身份号码"]["words"]}})
        # print("type", img_type)
        # print("upload_url", upload_url)
        # print("local_url", local_url)
        # print("abs_url", abs_url)
        return Response({"code": 0, "message": "success",
                         "data": {"url": local_url, "abs_url": abs_url}})

    def get_instance(self):
        user_id = self.request.user['user_id']
        return models.CompanyAuth.objects.filter(company_id=user_id).first()

    def perform_create(self, serializer):
        user_id = self.request.user['user_id']
        instance = serializer.save(company_id=user_id, remark="")
        instance.company.auth_type = 2
        instance.company.save()

    def perform_update(self, serializer):
        instance = serializer.save(remark="")
        instance.company.auth_type = 2
        instance.company.save()
