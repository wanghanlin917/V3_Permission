from django.urls import path, include
from .views import acount, basic, auth, wallet

from rest_framework import routers

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users/info', basic.UserInfoView, basename="UserInfoView")
router.register(r'auth', auth.AuthView, basename="AuthView")
router.register(r'wallet', wallet.WalletView)
router.register(r'wallet/tran', wallet.TranView)

urlpatterns = [
    path('users/login', acount.LoginView.as_view(), name='LoginView'),
    path('users/sms', acount.SendSmsView.as_view(), name='SendSmsView'),
    path('users/mobilelogin', acount.SmsLoginView.as_view(), name='SmsLoginView'),
    path('', include(router.urls)),
    path('users/register', acount.RegisterView.as_view(), name='RegisterView'),

    path('wallet/charge/notify', wallet.ChargeNotifyView.as_view()),
]
urlpatterns += router.urls
