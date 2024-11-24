from rest_framework.response import Response
from django.http.response import Http404


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
             "data": serializer.data})


class ListRetrieveModelMixin:
    def list(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {"code": 0, "message": "成功",
                 "data": serializer.data})
        except Http404 as e:
            return Response({"code": -1, "message": "对象不存在"})
        except Exception as e:
            print(e)
            return Response({"code": -1, "message": "钱包错误"})


class RetrieveModelMixin:
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            print("re", serializer.data)
            return Response({"code": 0, "message": "成功", "data": serializer.data})
            # return Response(
            #     {"code": 0, "message": "成功",
            #      "data": {"id": instance.id, "username": instance.username, "email": instance.email,
            #               "mobile": instance.mobile, "register_time": instance.ctime, "roles": ["admin"],
            #               "type": instance.auth_type}})
        except Http404 as e:
            return Response({"code": -1, "message": "对象不存在"})
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
            return Response({"code": 0, "message": "请求成功", "data": serializer.data})

        except Exception as e:
            return Response({"code": -1, "message": "请求失败"})

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class CreateUpdateModelMixin:
    def get_instance(self):
        """ 这是一个钩子，返回对象，则表示更新；返回None则表示新建"""
        pass

    def create(self, request, *args, **kwargs):
        instance = self.get_instance()
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({"code": -1, "message": serializer.errors})
            self.perform_update(serializer)
            return Response({"code": 0, "message": "提交成功", "data": serializer.data})
        else:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"code": -1, "message": serializer.errors})
            self.perform_create(serializer)
            return Response({"code": 0, "message": "提交成功", "data": serializer.data})

        def perform_create(self, serializer):
            serializer.save()

        def perform_update(self, serializer):
            serializer.save()


class ListPageNumberModelMixin:
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                "code": 0,
                "data": {"total": queryset.count(), 'page_size': self.paginator.page_size, "data": serializer.data}
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 0,
            "data": serializer.data
        })


class CreateModelMixin:
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(serializer.initial_data)
        # serializer.is_valid(raise_exception=True)
        print("验证", serializer.is_valid())
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({"code": -1, "message": serializer.errors})
        res = self.perform_create(serializer)
        return res or Response({"code": 0, "message": "发布成功", "data": serializer.data})

    def perform_create(self, serializer):
        serializer.save()
