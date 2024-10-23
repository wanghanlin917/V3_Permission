from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from utils.jwt_auth import parse_payload
from utils.jwt_auth import create_token,parse_payload


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
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'API realm="API"'


class JwtParamAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 1.读取请求头的token
        authorization = request.query_params.get('Authorization')
        # 2.token验证
        status, info_or_error = parse_payload(authorization)
        # 3.校验失败，继续往后走
        if not status:
            return
        # 4.校验成功继续往后 request.user request.auth
        return (info_or_error, authorization)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return 'API realm="API"'

    class DenyAuthentication(BaseAuthentication):
        def authenticate(self, request):
            raise exceptions.AuthenticationFailed({'code': 8888, 'msg': "认证失败"})

        def authenticate_header(self, request):
            return 'API realm="API"'




