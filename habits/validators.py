from rest_framework import serializers
from rest_framework.serializers import ValidationError


def validate_duration_for_useful_habit(duration, is_pleasant):
    """
    Валидирует время выполнения для полезных привычек.
    """
    if not is_pleasant:  # Валидация только для полезных привычек
        if duration is None:
            raise serializers.ValidationError(
                {"duration": "Для полезной привычки необходимо указать время на выполнение"}
            )
        if duration > 120:  # duration - это минуты
            raise ValidationError(
                {"duration": "Время на выполнение полезной привычки не должно превышать 120 секунд"}
            )
    if is_pleasant and duration is not None:
        raise ValidationError({"duration": "Приятная привычка не может иметь время на выполнение"})


def validate_periodicity_for_habit(periodicity_days, is_pleasant):
    """
    Валидирует периодичность выполнения привычки.
    """
    if not is_pleasant and not (1 <= periodicity_days <= 7):
        raise ValidationError({"periodicity_days": "Периодичность выполнения привычки должна быть от 1 до 7 дней"})


def validate_choose_reward_or_related_habit(is_pleasant, reward, related_habit):
    """
    Исключает одновременный выбор связанной привычки и указания вознаграждения.
    Применяется только для полезных привычек.
    """

    if not is_pleasant:
        if reward and related_habit:
            raise ValidationError(
                {
                    "reward": "Полезная привычка не может иметь одновременно и вознаграждение, и "
                    "связанную привычку. Выберите что-то одно.",
                    "related_habit": "Полезная привычка не может иметь одновременно и вознаграждение, и связанную "
                    "привычку. Выберите что-то одно.",
                }
            )
        # Дополнительно: полезная привычка должна иметь хоть что-то
        if not reward and not related_habit:
            raise ValidationError("Полезная привычка должна иметь либо вознаграждение, либо связанную привычку.")


def validate_pleasant_habit_without_reward_and_related_habit(is_pleasant, reward, related_habit):
    """
    Валидирует отсутствие вознаграждения или связанной привычки для приятной привычки
    """

    if is_pleasant:
        if reward:
            raise ValidationError({"reward": "Приятная привычка не может иметь вознаграждение."})
        if related_habit:
            raise ValidationError({"related_habit": "Приятная привычка не может быть связана с другой привычкой."})


def validate_related_habit_must_be_pleasant(related_habit):
    """
    Валидирует наличие признака приятной привычки у связанной привычки
    """
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError({"related_habit": "Связанная привычка должна быть приятной привычкой."})
