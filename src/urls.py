from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView, SpectacularRedocView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication

api = 'v1'
schema_view = get_schema_view(
    openapi.Info(
        title="appointment app API Documentation",
        default_version='v1',
        description='Welcome to the appointment app Backend API reference! It contains a guide on how to integrate our API and '
                    'outlines important information to assist you through the integration process. The API is a REST '
                    'API over HTTP using JSON as the exchange format. It uses standard HTTP response codes, '
                    'authentication, and verbs.',
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="amosmaru10@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[JWTStatelessUserAuthentication],
)


third_party_urlpatterns = [
    path("ckeditor5/", include('django_ckeditor_5.urls')),

    # API documentation urls
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-schema'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

urlpatterns = [
                path('admin', admin.site.urls),
                path(f'auth/{api}/', include('account.urls')),
                path(f'appointments/{api}/', include('appointments.urls')),
                path(f'wallet/{api}/', include('walletApp.urls')),
                path(f'blogs/{api}/', include('blogs.urls')),
            ] + third_party_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.DEFAULT_FILE_STORAGE)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


websocket_urlpatterns = []
# handling error 404 and 500 (the error view is configured under utils folder)
handler404 = 'util.views.error_404'
handler500 = 'util.views.error_500'
