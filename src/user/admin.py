"""
File contains admin configuration for user app.
"""
from django.contrib import admin

from user.models import User

admin.site.register(User)
