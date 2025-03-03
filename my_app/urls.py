from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserView, LoginView, UserProfileView

urlpatterns=[
    path("create", UserView.as_view(), name="create"),
    path("login", LoginView.as_view(), name="login"),
    path("user_view", UserProfileView.as_view(), name="user_view"),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]