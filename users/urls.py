from django.urls import path
from rest_framework.permissions import AllowAny

from users.apps import UsersConfig
from users.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    UserCreateAPIView,
    UserDestroyAPIView,
    UserListAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("", UserListAPIView.as_view(), name="users_list"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user_retrieve"),
    path(
        "<int:pk>/delete/",
        UserDestroyAPIView.as_view(),
        name="user_delete",
    ),
    path(
        "<int:pk>/update/",
        UserUpdateAPIView.as_view(),
        name="user_update",
    ),
    path(
        "login/",
        CustomTokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        CustomTokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
]
