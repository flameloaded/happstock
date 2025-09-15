from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from .models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view,permission_classes


@api_view(["POST"])
def google_auth(request):
    token = request.data.get("token")
    if not token:
        return Response({"error": "Token not provided","status":False}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
    # Code goes here
        id_info = id_token.verify_oauth2_token(
        token, 
        google_requests.Request(), 
        settings.GOOGLE_OAUTH_CLIENT_ID
        )
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