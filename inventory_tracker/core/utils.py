from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

token_generator = PasswordResetTokenGenerator()

def generate_activation_link(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    # Example link: http://happstock.com/auth/activate/<uid>/<token>/
    activation_link = f"{request.scheme}://{request.get_host()}/auth/activate/{uid}/{token}/"
    return activation_link
