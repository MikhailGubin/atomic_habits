from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitTestCase(APITestCase):
    def setUp(self):
        """Создает базовый набор параметров для тестов для модели "habit" """
        self.user = User.objects.create(email="admin@example.com")
        self.user.set_password("12345")
        self.user.save()
        self.habit = Habit.objects.create(
            action="пить стакан воды",
            place="на кухне",
            time="18:00",
            duration="10",
            reward="купить десерт",
            owner=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def test_habit_retrieve(self):
        """Проверяет процесс просмотра одного объекта класса "Привычка" """
        url = reverse("habits:habits-retrieve", args=[self.habit.pk])
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("action"), self.habit.action)
