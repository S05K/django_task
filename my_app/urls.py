from django.urls import path
from .views import UserView, LoginView, UserProfileView

urlpatterns=[
    path("create", UserView.as_view(), name="create"),
    path("login", LoginView.as_view(), name="login"),
    path("user_view", UserProfileView.as_view(), name="user_view")
]