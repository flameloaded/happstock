from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from .models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view,permission_classes
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .utils import generate_activation_link, token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework import status, generics
from .serializers import SignupSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import sendgrid
from sendgrid.helpers.mail import Mail


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




class SignupView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            current_site = get_current_site(request)
            protocol = "https" if request.is_secure() else "http"
            activation_link = f"{protocol}://{current_site.domain}/auth/activate/{uid}/{token}/"

            mail_subject = "Activate your Happstock account"
            message = render_to_string("core/account_activation_email.html", {
                "user": user,
                "activation_link": activation_link,
            })

            try:
                sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
                email = Mail(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to_emails=serializer.validated_data["email"],
                    subject=mail_subject,
                    html_content=message
                )
                sg.send(email)

            except Exception as e:
                return Response(
                    {"detail": f"Account created but failed to send email: {str(e)}"},
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {"detail": "Account created successfully. Please check your email to activate your account."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account successfully activated. You can now log in."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired activation link."}, status=status.HTTP_400_BAD_REQUEST)






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