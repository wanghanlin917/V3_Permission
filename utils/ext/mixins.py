from rest_framework.response import Response


class RetrieveModelMixin:
    def retrieve(self, request, *args, **kwargs):
        print(request.data)
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({"code": 0, "message": "成功", "data": serializer.data})
            # return Response(
            #     {"code": 0, "message": "成功",
            #      "data": {"id": instance.id, "username": instance.username, "email": instance.email,
            #               "mobile": instance.mobile, "register_time": instance.ctime, "roles": ["admin"],
            #               "type": instance.auth_type}})
        except Exception as e:
            return Response({"code": -1, "message": "请求失败"})
