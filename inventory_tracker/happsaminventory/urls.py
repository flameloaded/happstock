from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Happstock API",
        default_version='v1',
        description="API documentation for Happstock Inventory",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)



router = routers.DefaultRouter()


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/", include('apps.core.urls')),
    path("api/userprofile/", include('apps.userprofile.urls')),
    path("api/", include("apps.businesses.urls")),
]

urlpatterns += [
   path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0)),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
