from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account import views
from account.views import RefreshTokenView, LoginView, CheckRefreshTokenValidity

app_name = 'account'
router = DefaultRouter(trailing_slash=False)
router.register(r'users', views.UsersView, basename='users')
# router.register('groups', views.GroupView, basename='groups')
# router.register('permissions', views.PermissionView , basename="permissions")


urlpatterns = [
    path('', include(router.urls)),
    path('signup', views.RegistrationView.as_view(), name='register'),
    path('signin', LoginView.as_view(), name='login'),
    path('token/refresh', RefreshTokenView.as_view(), name='token_refresh'),
    path('token/refresh/<str:refresh>/verify', CheckRefreshTokenValidity.as_view(), name='verify_refresh'),
    path('social-auth/', include('social_auth.urls', namespace='social-auth')),
    path('reset-password/<str:encoded_pk>/<str:token>', views.ResetPasswordView.as_view(),
         name='confirm-reset-password'),
    path('reset-password', views.PasswordReset.as_view(), name='reset-password'),
    path('account/verify', views.EmailVerification.as_view(), name='account-verification'),
    path('account/verify/confirm/<str:code>', views.CodeVerification.as_view(), name='account-verification-confirm'),
    path('account/verify/code', views.CodeView.as_view(), name='account-code'),
    ]
