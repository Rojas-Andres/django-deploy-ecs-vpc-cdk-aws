"""
File for the authentication serializer.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer class for user login credentials and JWT generation.

    This class extends the TokenObtainPairSerializer from the rest_framework_simplejwt library.
    It adds custom claims and data to the JWT payload, including the user's email, ID, name, and email.
    """

    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        """
        Validate the user's login credentials.

        Overrides the parent class method to add custom data to the response, including the user's ID, name, and email.

        Args:
            attrs: The user's login credentials.

        Returns:
            The validated data with custom data added to the response.
        """
        data = super().validate(attrs)

        # Add custom data to response
        data["id"] = self.user.id
        data["name"] = self.user.first_name + " " + self.user.last_name
        data["email"] = self.user.email

        return data
