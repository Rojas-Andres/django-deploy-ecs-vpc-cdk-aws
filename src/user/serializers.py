"""
File for the user serializer.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user.models import User

# Get the User model
UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user object.

    This class is responsible for serializing and deserializing User objects.
    It defines the metadata for the User model and specifies the fields to be included
    in the serialized representation of the model.
    It also provides methods for creating and updating User objects with encrypted passwords,
    and for representing User objects in a specific format.
    """

    class Meta:
        """
        Class for metadata.

        This class specifies the model to be serialized and the fields to be included in the serialized representation.
        Specifies extra keyword arguments for specific fields, such as write_only and min_length for the password field.
        """

        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """
        Create and return a user with encrypted password.

        This method creates a new User object using the validated data.
        If the email field is present in the validated data, it converts it to lowercase.
        The User object is then saved with the encrypted password and returned.
        """

        if validated_data.get("email"):
            validated_data["email"] = validated_data["email"].lower()
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return user.

        This method updates an existing User object with the validated data.
        If the password field is present in the validated data, it sets the new password and saves the User object.
        The updated User object is then returned.
        """

        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def to_representation(self, instance):
        """
        Method for representation of the user.

        This method represents a User object in a specific format.
        If the User object is not active, it raises a ValidationError.
        The User object is then represented as a dictionary with specific fields and their values.
        The dictionary is returned as the serialized representation of the User object.
        """

        if not instance.is_active:
            raise ValidationError({"error": "This user is not active"})
        data = {
            "id": instance.id,
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "document": instance.document,
            "phone_number": instance.phone_number,
            "is_active": instance.is_active,
            "created_at": instance.created_at,
        }
        return data


class CustomUserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the user object.

    This serializer is used to serialize user data and represent it in a structured format.
    It includes the metadata for the UserSerializer class, which defines the model to be serialized
    and the fields to be included in the serialized representation of the model.
    It provides a method for representing the user and raises a validation error if the user is not active.
    """

    class Meta:
        """
        Class for defining metadata for the UserSerializer class.

        Attributes:
            model: The model to be serialized.
            fields: The fields to be included in the serialized representation of the model.
        """

        model = get_user_model()
        fields = [
            "id",
            "email",
            "is_staff",
            "is_superuser",
            "first_name",
            "last_name",
            "phone_number",
            "profile_image",
        ]

    def to_representation(self, instance):
        """
        Return a serialized representation of the user.

        Args:
            instance: The user instance to be serialized.

        Returns:
            dict: A dictionary containing the serialized representation of the user.

        Raises:
            ValidationError: If the user is not active.

        """
        if not instance.is_active:
            raise ValidationError({"error": "This user is not active"})
        representation = super().to_representation(instance)
        data = {"data": representation}
        return data
