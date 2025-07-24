from django.db.models import Q  # Для более сложных запросов, если понадобится
from rest_framework import serializers

from .models import Habit  # Импортируем вашу модель Habit


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

    class Meta:
        model = Habit
        fields = "__all__"  # Или перечислите все поля явно, если хотите контролировать их порядок
        # fields = [
        #     'id', 'user', 'action', 'time', 'place', 'is_public',
        #     'is_pleasant', 'duration_minutes', 'reward', 'related_habit',
        #     'periodicity_days',
        # ]

    # --- Валидация на уровне объекта (методы validate) ---
    def validate(self, data):
        """
        Валидация на уровне объекта для проверки взаимосвязи полей.
        data содержит данные, которые пришли в запросе.
        self.instance содержит существующий объект, если это PUT/PATCH запрос.
        """
        # Получаем значения полей, учитывая, что в PATCH-запросе их может не быть
        is_pleasant = data.get("is_pleasant", self.instance.is_pleasant if self.instance else False)
        reward = data.get("reward", self.instance.reward if self.instance else None)
        related_habit = data.get("related_habit", self.instance.related_habit if self.instance else None)
        duration_minutes = data.get("duration_minutes", self.instance.duration_minutes if self.instance else None)
        periodicity_days = data.get("periodicity_days", self.instance.periodicity_days if self.instance else None)

        # 1. Исключить одновременный выбор связанной привычки и указания вознаграждения.
        #    Применимо только для полезных привычек.
        if not is_pleasant:
            if reward and related_habit:
                raise serializers.ValidationError(
                    {
                        "reward": "Полезная привычка не может иметь одновременно и вознаграждение, и "
                        "связанную привычку. Выберите что-то одно.",
                        "related_habit": "Полезная привычка не может иметь одновременно и вознаграждение, и связанную "
                        "привычку. Выберите что-то одно.",
                    }
                )
            # Дополнительно: полезная привычка должна иметь хоть что-то
            if not reward and not related_habit:
                raise serializers.ValidationError(
                    "Полезная привычка должна иметь либо вознаграждение, либо связанную привычку."
                )

        # 2. У приятной привычки не может быть вознаграждения или связанной привычки.
        if is_pleasant:
            if reward:
                raise serializers.ValidationError({"reward": "Приятная привычка не может иметь вознаграждение."})
            if related_habit:
                raise serializers.ValidationError(
                    {"related_habit": "Приятная привычка не может быть связана с другой привычкой."}
                )
            # Для приятных привычек duration_minutes не применяется и не должен быть заполнен
            if duration_minutes is not None:
                raise serializers.ValidationError(
                    {"duration_minutes": "Приятная привычка не может иметь время на выполнение."}
                )

        # 3. В связанные привычки могут попадать только привычки с признаком приятной привычки.
        #    Это уже частично сделано в поле related_habit, но лучше продублировать здесь для надежности
        #    и на случай, если кто-то попытается обойти фильтрацию поля.
        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError({"related_habit": "Связанная привычка должна быть приятной привычкой."})

        # 4. Время выполнения (duration_minutes) должно быть не больше 120 секунд (2 минуты).
        #    Применимо только для полезных привычек.
        if not is_pleasant:
            if duration_minutes is None:
                raise serializers.ValidationError(
                    {"duration_minutes": "Для полезной привычки необходимо указать время на выполнение."}
                )
            if duration_minutes > 2:  # В модели это минуты, 2 минуты = 120 секунд
                raise serializers.ValidationError(
                    {
                        "duration_minutes": "Время на выполнение полезной привычки не должно превышать "
                        "2 минуты (120 секунд)."
                    }
                )

        # 5. Нельзя выполнять привычку реже, чем 1 раз в 7 дней.
        #    Нельзя не выполнять привычку более 7 дней.
        #    Эти два пункта по сути означают, что периодичность должна быть от 1 до 7 дней включительно.
        if periodicity_days is not None:
            if not (1 <= periodicity_days <= 7):
                raise serializers.ValidationError(
                    {"periodicity_days": "Периодичность выполнения привычки должна быть от 1 до 7 дней."}
                )
        else:  # Если periodicity_days почему-то не пришел в данных, а по умолчанию его нет (хотя в модели он есть)
            raise serializers.ValidationError(
                {"periodicity_days": "Периодичность выполнения привычки должна быть указана."}
            )

        return data
