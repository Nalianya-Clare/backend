from django.urls import path
from social_auth import views

app_name = 'social_auth'

urlpatterns = [
    path("callback", views.GoogleLogin.as_view(), name="callback"),
    path("redirect", views.GoogleLoginRedirectApi.as_view(), name="redirect"),
]
