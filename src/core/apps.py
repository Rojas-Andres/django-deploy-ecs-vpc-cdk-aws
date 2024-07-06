"""
File for app configuration.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Class for app Core configuration.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
