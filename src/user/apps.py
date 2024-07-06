"""
File for configuration to user app.
"""
from django.apps import AppConfig


class UserConfig(AppConfig):
    """
    Class for app User configuration.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "user"
