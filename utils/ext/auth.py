from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from utils.jwt_auth import parse_payload


class JwtAuthentication(BaseAuthentication):

    def authenticate(self, request):
        if request.method == "OPTIONS":
            return
        # 1.读取请求头的token
        authorization = request.META.get('HTTP_AUTHORIZATION')
        # authorization = request.GET.get("authorization")
        # print(authorization)
        # print("11111")
        # print(request.GET)
        # 2.token校验
        # print("exit")
        status, info_or_error = parse_payload(authorization)
        # print(status, info_or_error)
        # 校验失败，返回失败消息
        if not status:
            # return Response({"code": 401, "message": info_or_error, "data": {"username": "", "roles": ""}})
            raise exceptions.AuthenticationFailed(
                {"code": 401, "message": info_or_error, "data": {"username": "", "roles": ""}})
        # 4.校验成功，继续向后 request.user, request.auth
        return (info_or_error, authorization)
        # return (1,2)
