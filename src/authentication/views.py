"""
File with the authentication views.
"""
import secrets

from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from authentication.models import OTP
from authentication.serializers import LoginSerializer
from core.utils import send_email
from user.models import User


class LoginView(TokenObtainPairView):
    """
    View for handling user authentication requests.

    This view allows users to log in by providing their email and password.
    Upon successful login, it returns a JSON response with the user's details and tokens.

    Inherits from TokenObtainPairView, which generates a JSON Web Token (JWT) for a user.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def handle_exception(self, exc):
        """
        Handle exceptions that occur during the authentication process.

        Overrides the handle_exception method of the parent class to handle AuthenticationFailed exceptions,
        which occur when the user provides incorrect login credentials.

        Args:
            exc: The exception that occurred.

        Returns:
            A JSON response with an error message and status code.

        """
        if isinstance(exc, AuthenticationFailed):
            return Response(
                {"message": "Error login, password incorrect", "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().handle_exception(exc)

    def post(self, request):
        """
        Handle POST requests for user authentication.

        Overrides the post method of the parent class to add custom functionality for user authentication.
        It checks if the email and password are provided, checks if the email exists in the database,
        and returns a custom response with the user's details and tokens upon successful login.

        Args:
            request: The HTTP request object.

        Returns:
            A JSON response with the user's details, tokens, and status code.

        """
        request_email = request.data.get("email")
        request_password = request.data.get("password")
        if not request_email or not request_password:
            return Response(
                {"message": "Error Email or Password not found", "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.data.get("email"):
            user = User.objects.filter(email=request.data["email"]).first()
            if not user:
                return Response(
                    {"message": "Error Email not found", "status": status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        response = super().post(request)

        refresh_token = response.data["refresh"]
        access_token = response.data["access"]
        user_id = response.data["id"]
        email = response.data["email"]
        name = response.data["name"]

        return Response(
            {
                "message": "User logged in successfully",
                "user_detail": {
                    "user_id": user_id,
                    "email": email,
                    "name": name,
                },
                "token": {
                    "refresh_token": refresh_token,
                    "access_token": access_token,
                },
                "status": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    A view for handling user logout requests.

    This view requires the user to be authenticated and expects a refresh token to be provided in the request data.
    Upon receiving a valid refresh token, the view invalidates it and logs the user out, returning a success message.
    If the token is invalid or an error occurs during the logout process, an appropriate error message is returned.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle the HTTP POST request sent to the LogoutView endpoint.

        This method expects a refresh token to be provided in the request data.
        If the token is valid, it is invalidated and the user is logged out.
        If the token is invalid or an error occurs, an appropriate error message is returned.

        Args:
            request: The HTTP request object.

        Returns:
            A Response object with a success message if the logout is successful,
            or an error message if the token is invalid or an error occurs during the logout process.
        """
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response(
                {"message": "Error refresh token not found", "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()

            return Response(
                {"message": "Successfully logged out.", "status": status.HTTP_205_RESET_CONTENT},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except TokenError:
            return Response(
                {"message": "Invalid token.", "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": "Error logout", "error": str(e), "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutAllView(APIView):
    """
    View for logging out all active sessions of a user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Invalidate all outstanding tokens for the authenticated user.

        If there are no active tokens for the user, return an error message.
        If the token is invalid, return an error message.
        If there is any other error, return an error message with details.

        Returns:
            A response with a success message if the operation is successful,
            or an error message if there are no active tokens for the user,
            the token is invalid, or there is any other error.
        """
        try:
            tokens = OutstandingToken.objects.filter(user_id=request.user.id)
            if not tokens:
                return Response(
                    {"message": "No active tokens for this user.", "status": status.HTTP_400_BAD_REQUEST},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)

            return Response(
                {"message": "Successfully logged out all sessions.", "status": status.HTTP_205_RESET_CONTENT},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except TokenError:
            return Response(
                {"message": "Invalid token.", "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"message": "Error logout", "error": e, "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SendOTPView(APIView):
    """
    View for sending OTP (One-Time Password) codes.
    """

    def post(self, request):
        """
        Send an OTP code to the user's phone number.
        """
        email = request.data.get("email", None)

        if not email:
            return Response({"error": "Email is required!"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "Email is not registered!"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active is False:
            return Response({"error": "User is not active"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        verification_code = secrets.randbelow(900000) + 100000

        # Save OTP
        otp = OTP.objects.create(user=user, code=verification_code, created_at=timezone.now())

        context = {
            "first_name": user.first_name,
            "otp_code_1": str(otp.code)[0],
            "otp_code_2": str(otp.code)[1],
            "otp_code_3": str(otp.code)[2],
            "otp_code_4": str(otp.code)[3],
            "otp_code_5": str(otp.code)[4],
            "otp_code_6": str(otp.code)[5],
            "otp_validity_duration": str(otp.validity_duration),
        }
        html_content = render_to_string("otp.html", context)
        to_send_email = [{"email": user.email, "name": user.first_name}]
        send_email(f"Your OTP code for APP_NAME login is {str(otp.code)}", html_content, to_send_email)

        return Response({"success": True, "message": "Code sent successfully!"})


class LoginOTPView(APIView):
    """
    A class-based view for handling user authentication using One-Time Password (OTP) codes.

    This view allows users to log in by providing their email and OTP code. Upon successful login,
    it returns a JSON response with the user's details and tokens.

    Methods:
    - post(): Handles the POST request for user authentication using OTP.
    - _handle_missing_fields(): Helper method to handle missing email and OTP fields.
    - _handle_otp_login(): Helper method to handle OTP login process.
    """

    def post(self, request):
        """
        Handles the POST request for user authentication using OTP.

        Args:
        - request: The HTTP request object.

        Returns:
        - response: The JSON response containing the user's details and tokens.
        - status_code: The HTTP status code of the response.
        """
        email = request.data.get("email", None)
        otp = request.data.get("otp", None)
        response = {}

        if not email or not otp:
            response, status_code = self._handle_missing_fields(email, otp)
        else:
            response, status_code = self._handle_otp_login(email, otp)

        return Response(response, status=status_code)

    def _handle_missing_fields(self, email, otp):
        """
        Helper method to handle missing email and OTP fields.

        Args:
        - email: The email provided by the user.
        - otp: The OTP code provided by the user.

        Returns:
        - response: The JSON response containing the error message.
        - status_code: The HTTP status code of the response.
        """
        missing_fields = []
        if not email:
            missing_fields.append("email")
        if not otp:
            missing_fields.append("OTP")
        if not otp and not email:
            missing_fields = ["email", "OTP"]
        error_message = f"Missing required fields: {', '.join(missing_fields)}"
        response = {"error": error_message}
        status_code = 400
        return response, status_code

    def _handle_otp_login(self, email, otp):
        """
        Helper method to handle OTP login process.

        Args:
        - email: The email provided by the user.
        - otp: The OTP code provided by the user.

        Returns:
        - response: The JSON response containing the user's details and tokens.
        - status_code: The HTTP status code of the response.
        """
        user = User.objects.filter(email=email).first()
        if not user:
            response = {"error": "Email not registered"}
            status_code = status.HTTP_404_NOT_FOUND
        elif user.is_active is False:
            response = {"error": "User is not active"}
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            # Check OTP
            otp = OTP.objects.filter(user=user, code=otp).first()
            if not otp:
                response = {"error": "Invalid OTP"}
                status_code = status.HTTP_400_BAD_REQUEST
            elif otp.is_expired():
                response = {"error": "OTP is expired"}
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                if otp.is_active:
                    access_token = str(AccessToken.for_user(user))
                    refresh_token = str(RefreshToken.for_user(user))

                    otp.is_active = False
                    otp.save()

                    response = {
                        "message": "User logged in successfully",
                        "user_detail": {
                            "user_id": user.id,
                            "email": user.email,
                            "name": user.first_name + " " + user.last_name,
                        },
                        "token": {
                            "refresh_token": refresh_token,
                            "access_token": access_token,
                        },
                        "status": 200,
                    }

                    status_code = status.HTTP_200_OK
                else:
                    response = {"error": "OTP is not active, please request a new one."}
                    status_code = status.HTTP_400_BAD_REQUEST

        return response, status_code
