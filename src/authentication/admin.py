"""
File contains admin configuration for authentication app.
"""
from django.contrib import admin

from authentication.models import OTP

admin.site.register(OTP)
