from django.urls import path

from habits.apps import HabitsConfig
from habits.views import (
    HabitCreateAPIView,
    HabitDestroyAPIView,
    HabitOwnerListAPIView,
    HabitRetrieveAPIView,
    HabitUpdateAPIView,
    PublicHabitListAPIView
)

app_name = HabitsConfig.name

urlpatterns = [
    path("habits/public/", PublicHabitListAPIView.as_view(), name="public-habits-list"),
    path("habits/", HabitOwnerListAPIView.as_view(), name="habits-list"),
    path("habits/<int:pk>/", HabitRetrieveAPIView.as_view(), name="habits-retrieve"),
    path("habits/create/", HabitCreateAPIView.as_view(), name="habits-create"),
    path("habits/<int:pk>/delete/", HabitDestroyAPIView.as_view(), name="habits-delete"),
    path("habits/<int:pk>/update/", HabitUpdateAPIView.as_view(), name="habits-update"),
]
