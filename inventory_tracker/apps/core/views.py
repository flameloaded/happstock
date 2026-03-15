from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from .models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings

from rest_framework import status
from .serializers import SignupSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string

from sendgrid.helpers.mail import Mail
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import sendgrid
from django.core.cache import cache
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from sendgrid.helpers.mail import Mail
from .serializers import SignupSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
import sendgrid
from sendgrid.helpers.mail import Mail
from apps.core.models import User
from apps.core.serializers import SignupSerializer  # adjust import if needed
from django.core.mail import EmailMultiAlternatives

from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
User = get_user_model()
from .utils import send_verification_email, send_password_reset_email
from django.utils import timezone
from datetime import timedelta


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"message": "Logged out successfully"})

    except Exception:
        return Response(
            {"error": "Invalid token"},
            status=status.HTTP_400_BAD_REQUEST
        )


@csrf_exempt
@api_view(["POST"])
def google_auth(request):
    token = request.data.get("token")
    if not token:
        return Response({"error": "Token not provided","status":False}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
    # Code goes here
        id_info = id_token.verify_oauth2_token(
        token,
        google_requests.Request()
        )

# Ensure the token was issued for one of your apps
        if id_info['aud'] not in settings.GOOGLE_OAUTH_CLIENT_IDS:
            return Response({"error": "Invalid client ID", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        email = id_info['email']
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        profile_pic_url = id_info.get('picture', '')

        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()
            user.first_name = first_name
            user.last_name = last_name
            user.registration_method = 'google'
            user.is_active = True
            user.save()
        else:
            if user.registration_method != 'google':
                return Response({
                    "error": "User needs to sign in through email",
                    "status": False
                }, status=status.HTTP_403_FORBIDDEN)
        
        refresh = RefreshToken.for_user(user)
        return Response(
            {
        "tokens": {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        "status": True
        },
    status=status.HTTP_200_OK
)
    

    except ValueError:
        return Response({"error": "Invalid token","status":False}, status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET'])
def Home(request):

    return Response("Hello world")







class SignupView(APIView):
    """
    Handles new user signup and sends an email verification code.
    Ensures case-insensitive email uniqueness and prevents duplicate code generation before expiry.
    """

    def post(self, request):

        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"].lower()

        # Ensure email uniqueness regardless of case
        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"error": "An account with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create inactive user
        user = serializer.save(email=email, is_active=False)

        # Generate verification code
        code = user.generate_verification_code()

        # NEW: save when code was sent
        user.last_code_sent_at = timezone.now()  # ✅ NEW FIELD
        user.save()

        try:

            send_verification_email(user, code)  # ✅ UPDATED (reusable email function)

            return Response(
                {
                    "detail": "Account created successfully. Please check your email for the verification code."
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:

            print("Email sending failed:", str(e))

            return Response(
                {
                    "detail": "Account created successfully.",
                    "verification_code": code,
                    "note": "Email service unavailable. Verification code returned in response."
                },
                status=status.HTTP_201_CREATED,
            )







class ActivateAccountView(APIView):

    def post(self, request):


        # Extract safely
        email = request.data.get("email")
        code = request.data.get("verification_code")

        # Validate inputs properly
        if not email or not code:
            return Response({"error": "Email and code are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Use your model’s built-in verify_code() logic
        if user.verify_code(code):
            user.is_active = True
            user.verification_code = None
            user.code_expires_at = None
            user.save(update_fields=["is_active", "verification_code", "code_expires_at"])
            return Response({"message": "Account successfully verified!"}, status=status.HTTP_200_OK)
        else:
            # Check why it failed
            if user.code_expires_at and timezone.now() > user.code_expires_at:
                return Response({"error": "Verification code has expired."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)






class EmailLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if not user.is_active:
                return Response({"error": "Please verify your email before logging in."}, status=status.HTTP_403_FORBIDDEN)

            # generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

    



class ResendVerificationCodeView(APIView):

    def post(self, request):

        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email__iexact=email)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_active:
            return Response(
                {"error": "Account already verified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        # NEW: rate limit resend (1 minute)
        if user.last_code_sent_at and user.last_code_sent_at > timezone.now() - timedelta(minutes=1):

            remaining_seconds = int(
                (user.last_code_sent_at + timedelta(minutes=1) - timezone.now()).total_seconds()
            )

            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60

            return Response(
                {
                    "error": f"Please wait {minutes} minute(s) and {seconds} second(s)"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate new code
        code = user.generate_verification_code()

        # Update last sent time
        user.last_code_sent_at = timezone.now()
        user.save()

        try:

            send_verification_email(user, code)

        except Exception as e:

            print("Resend email failed:", str(e))

            return Response(
                {
                    "verification_code": code,
                    "note": "Email service unavailable"
                }
            )

        return Response(
            {"detail": "Verification code resent successfully"}
        )
        




class RequestPasswordResetView(APIView):
    """
    Handles sending password reset verification codes via email.
    Ensures users cannot request a new code until the existing one expires.
    """

    def post(self, request):

        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # UPDATED: case-insensitive email check
            user = User.objects.get(email__iexact=email)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Prevent requesting new code before expiration
        if user.code_expires_at and timezone.now() < user.code_expires_at:

            remaining_seconds = int(
                (user.code_expires_at - timezone.now()).total_seconds()
            )

            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60

            return Response(
                {
                    "error": f"A code has already been sent. Please wait {minutes} minute(s) and {seconds} second(s)."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.is_active is False:
            return Response(
                {"error": "Account not activated yet."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Generate new verification code
        code = user.generate_verification_code()

        # NEW: track last time code was sent
        user.last_code_sent_at = timezone.now()
        user.save()

        try:

            # UPDATED: reusable email function
            send_password_reset_email(user, code)

        except Exception as e:

            return Response(
                {"error": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "Password reset code sent to your email."},
            status=status.HTTP_200_OK
        )
    
class ResendPasswordResetCodeView(APIView):

    def post(self, request):

        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email__iexact=email)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # NEW: rate limit resend (1 minute)
        if user.last_code_sent_at and user.last_code_sent_at > timezone.now() - timedelta(minutes=1):

            return Response(
                {"error": "Please wait {minutes} minute(s) to resend another code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate new reset code
        code = user.generate_verification_code()

        user.last_code_sent_at = timezone.now()
        user.save()

        try:

            send_password_reset_email(user, code)

        except Exception as e:

            return Response(
                {
                    "note": "Email failed, returning code.",
                    "code": code
                }
            )

        return Response(
            {"message": "Password reset code resent successfully."},
            status=status.HTTP_200_OK
        )


class VerifyResetCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response({"error": "Email and code are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if (
            user.verification_code == code and
            user.code_expires_at and
            timezone.now() < user.code_expires_at
        ):
            return Response({"message": "Code verified. You can now reset your password."}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid or expired code."}, status=status.HTTP_400_BAD_REQUEST)




class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("new_password")

        if not all([email, code, new_password]):
            return Response({"error": "Email, code, and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate code
        if (
            user.verification_code != code or
            not user.code_expires_at or
            timezone.now() > user.code_expires_at
        ):
            return Response({"error": "Invalid or expired code."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.verification_code = None
        user.code_expires_at = None
        user.save()

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
