from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Inventory API",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



router = routers.DefaultRouter()


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path('', include('core.urls')),
    path('api/userprofile/', include('userprofile.urls')),
]

urlpatterns += [
   path("swagger/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
