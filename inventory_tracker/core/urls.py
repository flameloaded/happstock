from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import SignupView,EmailLoginView,ActivateAccountView

urlpatterns = [

    path('', views.Home),
    path('google_login/', views.google_auth),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/login/", EmailLoginView.as_view(), name="login"),
    path("auth/activate/<uidb64>/<token>/", ActivateAccountView.as_view(), name="activate"),

]
