from django.urls import path
from .views import LoginView,UserInfo

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('users/login', LoginView.as_view(), name='LoginView'),
    path('users/info', UserInfo.as_view(), name='UserInfo')
]
