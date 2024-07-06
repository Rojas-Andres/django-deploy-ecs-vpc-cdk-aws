"""
File that contains the urls of the user app.
"""
from django.urls import path

from user.views import UserDetailView, UserListView, UserView

APP_NAME = "user"

urlpatterns = [
    path("", UserView.as_view(), name="user_list"),
    path("list/", UserListView.as_view(), name="user_list"),
    path("detail/", UserDetailView.as_view(), name="user_detail"),
]
