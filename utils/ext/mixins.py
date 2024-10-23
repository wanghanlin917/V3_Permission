from rest_framework.response import Response


class ListModelMixin:
    """
    List a queryset.
    """

    def list(self, request, *args, **kwargs):
        instance = self.filter_queryset(self.get_queryset())
        #
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(instance, many=True)
        print(serializer.data)
        return Response(
            {"code": 0, "message": "成功",
             "data": ""})


class RetrieveModelMixin:
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            # print(serializer.data)
            return Response({"code": 0, "message": "成功", "data": serializer.data})
            # return Response(
            #     {"code": 0, "message": "成功",
            #      "data": {"id": instance.id, "username": instance.username, "email": instance.email,
            #               "mobile": instance.mobile, "register_time": instance.ctime, "roles": ["admin"],
            #               "type": instance.auth_type}})
        except Exception as e:
            print(e)
            return Response({"code": -1, "message": "jajaj"})


class UpdateModelMixin:
    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            # serializer.is_valid(raise_exception=True)
            if not serializer.is_valid():
                print(serializer.errors)
                key = list(serializer.errors.keys())[0]
                return Response({"code": -1, "message": serializer.errors[key][0]})
            # print("新的",serializer.data)
            self.perform_update(serializer)
            return Response({"code": 0, "message": "请求成功","data":serializer.data})

        except Exception as e:
            return Response({"code": -1, "message": "请求失败"})

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
