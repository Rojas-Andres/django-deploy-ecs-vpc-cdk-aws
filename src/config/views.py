"""
Modules for setup views
"""

from django.http.response import HttpResponse
from rest_framework.views import APIView

from config.settings.base import ENVIRONMENT


class HealtCheck(APIView):
    """
    Greetings view used for the health check.
    """

    def get(self, request):
        """
        Greetings view used for the health check.
        """
        return HttpResponse(f"Stack Django v1.0 is up and running in {ENVIRONMENT} environment.")
