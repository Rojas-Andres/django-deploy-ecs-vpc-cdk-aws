"""
File with the user views.
"""

import os

from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils import send_email
from user.models import User
from user.serializers import UserSerializer


class UserView(APIView):
    """
    A view for handling user creation and update requests.

    This view allows users to be created and updated. It performs validation checks to ensure that the email address
    provided is unique and sends a welcome email to the user upon successful creation.

    Methods:
    - post: Create a new user.
    - put: Update an existing user.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Create a new user.

        This method handles HTTP POST requests to create a new user. It performs validation checks to ensure that the
        email address provided is unique. Upon successful creation, it sends a welcome email to the user.

        Returns:
        - Response: A response indicating the success or failure of the user creation.
        """
        if request.data.get("email"):
            user = User.objects.filter(email=request.data["email"]).first()
            if user:
                return Response(
                    {"message": "Error creating user, email already exists"}, status=status.HTTP_400_BAD_REQUEST
                )
        if request.data.get("phone_number") and request.data.get("code_phone"):
            user = User.objects.filter(
                phone_number=request.data["phone_number"], code_phone=request.data["code_phone"]
            ).first()
            if user:
                return Response(
                    {"message": "Error creating user, phone number already exists"}, status=status.HTTP_400_BAD_REQUEST
                )
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()

                context = {"first_name": request.data["first_name"], "url_frontend": os.environ.get("URL_FRONTEND")}
                html_content = render_to_string("welcome.html", context)
                to_send_email = [{"email": request.data["email"], "name": request.data["first_name"]}]
                send_email("Welcome to Name_APP", html_content, to_send_email)

                return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"message": "Error creating user", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update an existing user.

        This method handles HTTP PUT requests to update an existing user. It performs validation checks to ensure that
        the user being updated exists and that the email address provided is unique.

        Returns:
        - Response: A response indicating the success or failure of the user update.
        """
        user_id = self.request.data.get("id", self.request.user.id)
        if not user_id:
            return Response({"message": "User id not found"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"message": f"User with id {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        if request.data.get("email"):
            user = User.objects.filter(email=request.data["email"]).first()
            if user and user.id != user_id:
                return Response(
                    {"message": "Error updating user, email already exists"}, status=status.HTTP_400_BAD_REQUEST
                )
        if request.data.get("phone_number") and request.data.get("code_phone"):
            user = User.objects.filter(
                phone_number=request.data["phone_number"], code_phone=request.data["code_phone"]
            ).first()
            if user and user.id != user_id:
                return Response(
                    {"message": "Error updating user, phone number already exists"}, status=status.HTTP_400_BAD_REQUEST
                )
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)
        return Response(
            {"message": "Error updating user", "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class UserListView(APIView):
    """
    A view for retrieving a list of all users.
    Requires authentication to access the view.
    """

    permission_classes = [IsAuthenticated]

    def get(self):
        """
        Handles the GET request and retrieves all users.

        Returns:
            A Response object with the serialized user data and a status code of 200.
        """
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    """
    A view that returns the details of a user.

    Requires authentication and can receive a user id as a query parameter or use the id of the authenticated user.
    It returns a serialized representation of the user object if it exists, or an error message if it doesn't.
    """

    permission_classes = [IsAuthenticated]

    def get(self):
        """
        Retrieve the details of the user logged in.

        If a user id is provided as a query parameter, it will retrieve the user with that id.
        If no user id is provided, it will retrieve the user with the id of the authenticated user.

        Returns:
        - If the user is found, it returns a serialized representation of the user object with a status code of 200.
        - If the user id is not found, it returns an error message with a status code of 400.
        - If the user with the provided id is not found, it returns an error message with a status code of 404.
        """
        user_id = self.request.query_params.get("id", self.request.user.id)
        if not user_id:
            return Response({"message": "User id not found"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"message": f"User with id {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
