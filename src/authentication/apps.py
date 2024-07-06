"""
File to configure the authentication app.
"""
from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Class to configure the authentication app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
