from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (SignupView,
                    EmailLoginView,
                    ActivateAccountView,
                    ResendVerificationCodeView,
                    RequestPasswordResetView,
                    VerifyResetCodeView,
                    ResetPasswordView)



urlpatterns = [

    path('', views.Home),
    path('google_login/', views.google_auth),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/signup/", SignupView.as_view(), name="signup"),
    path("auth/login/", EmailLoginView.as_view(), name="login"),
    path("auth/verify/", ActivateAccountView.as_view(), name="activate"),
    path("auth/resend-code/", ResendVerificationCodeView.as_view(), name="resend-verification-code"),
    path("auth/request-password-reset/", RequestPasswordResetView.as_view(), name="request-password-reset"),
    path("auth/verify-reset-code/", VerifyResetCodeView.as_view(), name="verify-reset-code"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),

]
