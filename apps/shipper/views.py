from django.shortcuts import render
from rest_framework.response import Response
from django.http.response import JsonResponse
from rest_framework.views import APIView
import json


class LoginView(APIView):
    def post(self, request):
        print(request.data)
        return Response({"code": 0, "message": "成功", "data": {"token": "admindddd"}})


class UserInfo(APIView):
    def get(self, request):
        return Response({"code": 0, "message": "成功", "data": {"username": "admin", "role": "admin"}})
