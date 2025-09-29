from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import google_test

urlpatterns = [

    path('', views.Home),
    path('google_login/', views.google_auth),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('test-google/', google_test, name='test-google'),
]
