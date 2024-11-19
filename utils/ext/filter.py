from rest_framework.filters import BaseFilterBackend


class MineBaseFilter(BaseFilterBackend):
    MINE_FILED = "id"

    def filter_queryset(self, request, queryset, view):
        user_id = request.user.get('user_id')
        if user_id is None:
            return queryset.none()  # 如果用户ID不存在，返回空查询表
        return queryset.filter(**{self.MINE_FILED: user_id})


class MineFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not request.user:
            return queryset
        # # {'user_id': 1, 'name': '大和实业', 'exp': 1670212872}
        user_id = request.user.get('user_id')
        if user_id:
            return queryset.filter(id=user_id)
        return queryset
