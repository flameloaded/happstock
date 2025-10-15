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
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .serializers import SignupSerializer


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





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
import sendgrid
from sendgrid.helpers.mail import Mail
from core.models import User
from core.serializers import SignupSerializer  # adjust import if needed


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

        # 🔹 Ensure email uniqueness regardless of case
        if User.objects.filter(email__iexact=email).exists():
            return Response(
                {"error": "An account with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 🔹 Create inactive user
        user = serializer.save(email=email, is_active=False)

        # 🔹 Check if a valid verification code already exists
        if user.code_expires_at and timezone.now() < user.code_expires_at:
            remaining_time = int(
                (user.code_expires_at - timezone.now()).seconds / 60
            )
            return Response(
                {"error": f"A verification code has already been sent. Please wait {remaining_time} minute(s) before requesting another."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 🔹 Generate verification code
        code = user.generate_verification_code()

        # 🔹 Render email HTML
        html_message = render_to_string(
            "core/account_activation_email.html",
            {
                "user": user,
                "verification_code": code,
                "expiry_minutes": 10,
            },
        )

        # 🔹 Send email via SendGrid
        try:
            sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            email_msg = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=user.email,
                subject="Verify your Happstock account",
                html_content=html_message,
            )
            sg.send(email_msg)

        except Exception as e:
            return Response(
                {"detail": f"Account created but failed to send verification code: {str(e)}"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"detail": "Account created successfully. Please check your email for the verification code."},
            status=status.HTTP_201_CREATED,
        )



User = get_user_model()


from django.utils import timezone

class ActivateAccountView(APIView):
    def post(self, request):
        print("Received data:", request.data)  # debug

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
        print("📩 ResendVerificationCodeView triggered")  # debug
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            new_code = user.resend_verification_code()

            # ✅ Render HTML content using Django template
            html_content = render_to_string(
                "core/verification_email.html",
                {"user": user, "code": new_code}
            )

            # ✅ Send email via SendGrid
            sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            email_msg = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=user.email,
                subject="Your new Happstock verification code",
                html_content=html_content,
            )
            sg.send(email_msg)

            return Response(
                {"message": "A new verification code has been sent to your email."},
                status=status.HTTP_200_OK
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


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

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate or reuse verification code
        try:
            # Prevent multiple requests before expiration
            if user.code_expires_at and timezone.now() < user.code_expires_at:
                remaining_time = int((user.code_expires_at - timezone.now()).seconds / 60)
                return Response(
                    {"error": f"A code has already been sent. Please wait {remaining_time} minute(s) before requesting another."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate a new verification code
            code = user.generate_verification_code()

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Render email template
        html_message = render_to_string("core/password_reset_email.html", {
            "user": user,
            "code": code,
        })

        # Send email using SendGrid
        try:
            sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            email_msg = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=user.email,
                subject="Password Reset Code",
                html_content=html_message,
            )
            sg.send(email_msg)
        except Exception as e:
            return Response(
                {"error": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": "Password reset code sent to your email."},
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
