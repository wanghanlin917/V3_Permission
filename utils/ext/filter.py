from rest_framework.filters import BaseFilterBackend


class MineFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not request.user:
            return queryset
        # # {'user_id': 1, 'name': '大和实业', 'exp': 1670212872}
        user_id = request.user.get('user_id')
        if user_id:
            return queryset.filter(id=user_id)
        return queryset