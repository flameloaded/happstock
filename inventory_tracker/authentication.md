# Authentication Endpoints
1. Signup (Create Account)
Creates a new user account and sends a verification code to the user's email.
The account remains inactive until the verification code is confirmed.

Endpoint
# POST /api/auth/signup/
Request Body
{
  "email": "user@gmail.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}

# Response
{
  "detail": "Account created successfully. Please check your email for the verification code."
}

# 2. Verify Account (Activate Account)

# Activates the user account using the verification code sent via email.

Endpoint
POST /api/auth/verify/
Request Body

{
  "email": "user@gmail.com",
  "verification_code": "123456"
}


Success Response
{
  "message": "Account successfully verified!"
}

Error Response
{
  "error": "Invalid verification code."
}

# 3. Resend Verification Code

Allows the user to request a new email verification code.
A new code cannot be requested until the current code expires.

Endpoint
POST /api/auth/resend-code/
Request Body

{
  "email": "user@gmail.com"
}

Response
{
  "message": "A new verification code has been sent to your email."
}

# 4. Email Login

Authenticates a user using email and password.

Returns JWT access and refresh tokens.

Endpoint
POST /api/auth/login/
Request Body
{
  "email": "user@gmail.com",
  "password": "password123"
}

Success Response
{
  "refresh": "jwt_refresh_token",
  "access": "jwt_access_token"
}

Error Response
{
  "error": "Invalid credentials"
}

# 5. Google Login

Allows users to authenticate using Google OAuth.

The frontend should send the Google ID token obtained from Google Sign-In.
If the user does not exist, an account will be automatically created.

Endpoint
POST /api/google_login/
Request Body
{
  "token": "google_id_token"
}

Response
{
  "tokens": {
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token"
  },
  "status": true
}

# 6. Logout

Logs the user out by blacklisting the refresh token.
Requires authentication.

Endpoint
POST /api/auth/logout/
Headers
Authorization: Bearer <access_token>
Request Body

{
  "refresh": "refresh_token"
}

Response
{
  "message": "Logged out successfully"
}

Password Reset Flow
The password reset process follows three steps.

# 7. Request Password Reset Code

Sends a password reset verification code to the user's email.

Endpoint
POST /api/auth/request-password-reset/
Request Body

{
  "email": "user@gmail.com"
}

Response
{
  "message": "Password reset code sent to your email."
}

# 8. Verify Reset Code

Verifies the password reset code before allowing password reset.

Endpoint
POST /api/auth/verify-reset-code/
Request Body
{
  "email": "user@gmail.com",
  "code": "123456"
}
Response
{
  "message": "Code verified. You can now reset your password."
}

# 9. Reset Password

Updates the user's password after verifying the reset code.

Endpoint
POST /api/auth/reset-password/
Request Body
{
  "email": "user@gmail.com",
  "code": "123456",
  "new_password": "newpassword123"
}

Response
{
  "message": "Password reset successful."
}

JWT Token Endpoints

These endpoints come from Django REST Framework SimpleJWT.

# 10. Obtain JWT Token

Generates access and refresh tokens.

Endpoint
POST /api/api/token/
Request Body
{
  "email": "user@gmail.com",
  "password": "password123"
}

# 11. Refresh JWT Token

Generates a new access token using a refresh token.

Endpoint
POST /api/api/token/refresh/
Request Body
{
  "refresh": "refresh_token"
}



Typical user authentication flow:

Signup
   ↓
Receive email verification code
   ↓
Verify account
   ↓
Login
   ↓
Receive JWT tokens
   ↓
Use access token for authenticated requests