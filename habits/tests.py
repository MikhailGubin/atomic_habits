from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitUnauthorizedTestCase(APITestCase):
    def setUp(self):
        """Создает базовый набор параметров для тестов для модели "habit" """
        # Создание Пользователя
        self.user = User.objects.create(email="admin@example.com")
        self.user.set_password("12345")
        self.user.save()

        # Создание тестовой привычки 1
        self.habit = Habit.objects.create(
            action="пить стакан воды",
            place="на кухне",
            time="18:00",
            duration=10,
            reward="купить десерт",
            owner=self.user,
        )

    def test_create_habit_unauthorized(self):
        """Проверяет попытку создания привычки без авторизации."""
        url = reverse("habits:habits-create")
        habit_data = {
            'action': 'Бегать',
            'duration': 130,
            'time': '17:50',
            'place': 'Стадион',
            'owner': self.user.id,
            'reward': 'Съесть мороженное',
        }
        response = self.client.post(url, habit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_update_habit_unauthorized(self):
        """Проверяет попытку редактирования привычки без авторизации."""
        url = reverse("habits:habits-update", kwargs={"pk": self.habit.pk})
        new_data = {'action': 'подтягиваться'}
        response = self.client.patch(url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_habit_unauthorized(self):
            """Проверяет попытку удаления привычки без авторизации."""
            url = reverse("habits:habits-delete", kwargs={"pk": self.habit.pk})
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_user_habits_unauthenticated(self):
        """Проверяет попытку получить список привычек без авторизации."""
        url = reverse("habits:habits-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class HabitTestCase(APITestCase):

    def setUp(self):
        """Создает базовый набор параметров для тестов для модели "habit" """
        # Создание Пользователя
        self.user = User.objects.create(email="admin@example.com")
        self.user.set_password("12345")
        self.user.save()
        self.client.force_authenticate(user=self.user)

        # Создание тестовой привычки 1
        self.habit = Habit.objects.create(
            action="пить стакан воды",
            place="на кухне",
            time="18:00",
            duration=10,
            reward="купить десерт",
            owner=self.user,
        )

        # Создание другого Пользователя
        self.other_user = User.objects.create(
            email='other_user@example.com',
            password='45678'
        )
        self.other_user.save()

        # Создание другой привычки для тестов на списки и редактирование/удаление
        self.public_habit_other_user = Habit.objects.create(
            action="заниматься спортом",
            place="где-то",
            time="10:00",
            duration=5,
            periodicity_days=1,
            is_pleasant=False,
            is_public=True,
            reward="Похвалить себя",
            owner=self.other_user,
        )

    def test_habit_retrieve(self):
        """Проверяет процесс просмотра одного объекта класса "Привычка" """
        url = reverse("habits:habits-retrieve", args=[self.habit.pk])

        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("action"), self.habit.action)
        self.assertEqual(data.get("owner"), self.user.id)

    def test_habit_create(self):
        """Проверяет процесс создания одного объекта класса "Привычка" """
        url = reverse("habits:habits-create")
        habit_data = {
            'action': "бегать",
            'place': "на беговой дорожке",
            'periodicity_days': 3,
            'time': "17:50",
            'duration': "115",
            'reward': "посмотреть видео в Интеренете",
            'owner': self.user.id,
        }
        response = self.client.post(url, habit_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 3)

        created_habit = Habit.objects.get(action="бегать")
        self.assertEqual(created_habit.place, "на беговой дорожке")
        self.assertEqual(created_habit.duration, 115)
        self.assertEqual(created_habit.owner, self.user)

    def test_create_habit_missing_required_fields(self):
        """Проверяет создание привычки с пропущенными обязательными полями."""
        url = reverse("habits:habits-create")
        habit_data = {
            # Пропускаем 'action', 'time', 'place'
            'reward': 'Съесть мороженное',
            'owner': self.user.id,
        }
        response = self.client.post(url, habit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('action', response.json())
        self.assertIn('time', response.json())
        self.assertIn('place', response.json())

    def test_create_habit_validation_error_duration(self):
        """Проверяет создание полезной привычки с недопустимой длительностью."""
        url = reverse("habits:habits-create")
        habit_data = {
            'action': 'Бегать',
            'duration': 130,
            'time': '17:50',
            'place': 'Стадион',
            'owner': self.user.id,
            'reward': 'Съесть мороженное',
        }
        response = self.client.post(url, habit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('duration', response.json())
        self.assertIn("Время на выполнение полезной привычки не должно превышать 120 секунд",
                      response.json()['duration'])

    def test_create_habit_validation_error_periodicity(self):
        """Проверяет создание привычки с недопустимой периодичностью."""
        url = reverse("habits:habits-create")
        habit_data = {
            'action': 'Бегать',
            'duration': 100,
            'time': '17:50',
            'place': 'Стадион',
            'owner': self.user.id,
            'reward': 'Съесть мороженное',
            'periodicity_days': 8,  # > 7 дней
        }
        response = self.client.post(url, habit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('periodicity_days', response.json())
        self.assertIn("Периодичность выполнения привычки должна быть от 1 до 7 дней",
                      response.json()['periodicity_days'])


    def test_update_habit_success(self):
        """Проверяет успешное редактирование привычки."""
        # Используем self.habit (создана в setUp)
        url = reverse("habits:habits-update", kwargs={"pk": self.habit.pk})

        new_data = {
            'action': 'Обновленное действие',
            'duration': 45,
            'is_public': True,
            'reward': 'Обновленная награда',
            'owner': self.user.id,
            'time': '17:50',
            'place': 'Стадион',
        }
        response = self.client.put(url, new_data, format='json')  # Используем PUT для полного обновления

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('action'), new_data['action'])
        self.assertEqual(response.json().get('duration'), new_data['duration'])
        self.assertEqual(response.json().get('is_public'), new_data['is_public'])
        self.assertEqual(response.json().get('reward'), new_data['reward'])


    def test_update_habit_patch_success(self):
        """Проверяет успешное частичное редактирование привычки (PATCH)."""
        url = reverse("habits:habits-update", kwargs={"pk": self.habit.pk})
        new_data = {
            'action': 'Частично обновленное действие',
        }
        response = self.client.patch(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('action'), new_data['action'])
        # Проверяем, что другие поля остались прежними
        self.assertEqual(response.json().get('duration'), self.habit.duration)

    def test_update_habit_other_user(self):
        """Проверяет попытку редактирования привычки другого пользователя."""
        # Используем self.public_habit_other_user (привычка другого пользователя)
        url = reverse("habits:habits-update", kwargs={"pk": self.public_habit_other_user.pk})
        new_data = {'action': 'Попытка изменения'}

        response = self.client.put(url, new_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN])


    def test_update_habit_validation_error(self):
        """Проверяет редактирование привычки с недопустимыми данными."""
        url = reverse("habits:habits-update", kwargs={"pk": self.habit.pk})
        new_data = {
            'duration': 5,  # Допустимо
            'periodicity_days': 0,  # Недопустимо
        }
        response = self.client.patch(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Периодичность выполнения привычки должна быть от 1 до 7 дней",
                      response.json()['periodicity_days'])

    def test_delete_habit_success(self):
        """Проверяет успешное удаление привычки."""
        # Используем self.habit (создана в setUp)
        url = reverse("habits:habits-delete", kwargs={"pk": self.habit.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что привычка действительно удалена из базы данных
        self.assertFalse(Habit.objects.filter(id=self.habit.pk).exists())

    def test_delete_habit_other_user(self):
        """Проверяет попытку удаления привычки другого пользователя."""
        # Используем self.public_habit_other_user (привычка другого пользователя)
        url = reverse("habits:habits-delete", kwargs={"pk": self.public_habit_other_user.pk})

        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN])

# --- Тесты списка привычек текущего пользователя с пагинацией ---
    def test_list_user_habits_pagination(self):
        """Проверяет получение списка привычек пользователя с пагинацией."""

        for i in range(10, 15): # Создаем привычки с 10 по 15 (всего 5 новых)
            Habit.objects.create(
                owner=self.user,
                action=f'делать упражнение {i}',
                periodicity_days=1,
                place=self.habit.place,
                time=self.habit.time,
                duration=self.habit.duration,
                reward=self.habit.reward,

            )
        # Общее количество привычек пользователя = 1 (из setUp) + 5 (созданные здесь) = 6.
        url = reverse("habits:habits-list") # Предполагается 'habits-list' для списка привычек
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', data)

        self.assertEqual(len(data['results']), 5)
        self.assertEqual(data.get('count'), 6) # Проверим общее количество
        self.assertIn('next', data) # Проверяем наличие ссылки на следующую страницу
        self.assertIsNotNone(data.get('next'))

        # Тест второй страницы
        response_page2 = self.client.get(data.get('next'))
        data_page2 = response_page2.json()
        self.assertEqual(response_page2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data_page2['results']), 1)
        self.assertIn('previous', data_page2)
        self.assertIsNotNone(data_page2.get('previous'))

    # --- Список публичных привычек ---
    def test_list_public_habits(self):
        """Проверяет получение списка публичных привычек."""

        url = reverse("habits:public-habits-list")
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['results']), 1)

        habit_actions = [habit['action'] for habit in data['results']]
        self.assertIn("заниматься спортом", habit_actions)
        self.assertNotIn("пить стакан воды", habit_actions) # Проверяем, что приватная не попала
