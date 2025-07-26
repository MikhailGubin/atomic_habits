from rest_framework import serializers

from habits.models import Habit  # Импортируем вашу модель Habit
from habits.validators import (
    validate_choose_reward_or_related_habit,
    validate_duration_for_useful_habit,
    validate_periodicity_for_habit,
    validate_pleasant_habit_without_reward_and_related_habit,
    validate_related_habit_must_be_pleasant
)


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Habit с кастомными валидаторами.
    """

    # Если вы хотите, чтобы в UI/API для 'related_habit' отображались только приятные привычки,
    # и чтобы пользователю было легче выбрать, можно отфильтровать queryset здесь:
    related_habit = serializers.PrimaryKeyRelatedField(
        queryset=Habit.objects.filter(is_pleasant=True),  # Важно: Фильтруем только приятные привычки
        allow_null=True,  # Позволяет полю быть пустым
        required=False,  # Необязательное поле при создании/обновлении
        label="Связанная привычка",
        help_text="Приятная привычка, которая выполняется в качестве вознаграждения.",
    )
    duration = serializers.IntegerField(validators=[validate_duration_for_useful_habit], required=False)
    periodicity_days = serializers.IntegerField(validators=[validate_periodicity_for_habit], required=False)

    class Meta:
        model = Habit
        fields = [
            "id",
            "owner",
            "action",
            "time",
            "place",
            "is_public",
            "is_pleasant",
            "duration",
            "reward",
            "related_habit",
            "periodicity_days",
        ]

    # --- Валидация на уровне объекта (методы validate) ---
    def validate(self, data):
        """Валидация на уровне объекта для проверки взаимосвязи полей."""
        # data содержит данные, которые пришли в запросе.
        # self.instance содержит существующий объект, если это PUT/PATCH запрос.
        # Получаем значения полей, учитывая, что в PATCH-запросе их может не быть
        is_pleasant = data.get("is_pleasant", self.instance.is_pleasant if self.instance else False)
        reward = data.get("reward", self.instance.reward if self.instance else None)
        related_habit = data.get("related_habit", self.instance.related_habit if self.instance else None)

        # 1. Исключить одновременный выбор связанной привычки и указания вознаграждения.
        validate_choose_reward_or_related_habit(is_pleasant, reward, related_habit)

        # 2. У приятной привычки не может быть вознаграждения или связанной привычки.
        validate_pleasant_habit_without_reward_and_related_habit(is_pleasant, reward, related_habit)

        # 3. В связанные привычки могут попадать только привычки с признаком приятной привычки.
        validate_related_habit_must_be_pleasant(related_habit)

        return data
