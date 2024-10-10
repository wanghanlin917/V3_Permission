from django.urls import path, include
from .views import acount, basic

from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'users/info', basic.UserInfoView)

urlpatterns = [
    path('users/login', acount.LoginView.as_view(), name='LoginView'),
    path('users/sms', acount.SendSmsView.as_view(), name='SendSmsView'),
    path('users/mobilelogin', acount.SmsLoginView.as_view(), name='SmsLoginView'),
    # path('users/info', basic.UserInfo.as_view(), name='UserInfo'),
    path('', include(router.urls)),
    path('users/register', acount.RegisterView.as_view(), name='RegisterView')
]
# urlpatterns += router.urls
print("hahaha")
print(router.urls)
