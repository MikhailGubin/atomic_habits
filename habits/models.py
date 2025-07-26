from django.db import models
from django.utils import timezone


class Habit(models.Model):
    """Модель 'Привычка'"""

    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Создатель привычки",
        related_name="habits",
    )
    action = models.CharField(
        max_length=500,
        verbose_name="Действие",
        help_text="Что именно вы будете делать? (например, 'пить стакан воды')",
    )
    time = models.TimeField(
        verbose_name="Время",
        help_text="Когда выполнять привычку? (например, '18:00')",
    )
    place = models.CharField(
        max_length=255,
        verbose_name="Место",
        help_text="Где выполнять привычку? (например, 'на кухне')",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная привычка",
        help_text="Будет ли эта привычка видна другим пользователям?",
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="Является ли эта привычка приятной (используется как вознаграждение)?",
    )

    # --- Поля, зависящие от типа привычки (полезная/приятная) ---
    # Время на выполнение: только для полезных привычек
    duration = models.PositiveSmallIntegerField(
        verbose_name="Время на выполнение (сек.)",
        help_text="Время, которое предположительно потратит пользователь на выполнение привычки "
        "(не более 120 секунд).",
        blank=True,  # Может быть пустым, если is_pleasant=True
        null=True,  # Может быть NULL в БД
    )
    # Вознаграждение: для полезных привычек
    reward = models.CharField(
        max_length=255,
        verbose_name="Вознаграждение",
        help_text="Чем вознаградить себя после выполнения полезной привычки? (например, 'купить десерт')",
        blank=True,  # Может быть пустым, если есть related_habit или is_pleasant=True
        null=True,  # Может быть NULL в БД
    )
    # Связанная привычка: для полезных привычек (ссылка на приятную привычку)
    related_habit = models.ForeignKey(
        "self",  # Ссылка на саму себя
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        help_text="Приятная привычка, которая выполняется в качестве вознаграждения.",
        related_name="useful_habits_rewarded_by_me",  # Позволяет найти полезные привычки
    )
    # Периодичность
    periodicity_days = models.PositiveSmallIntegerField(
        default=1,  # По умолчанию ежедневно
        verbose_name="Периодичность (дни)",
        help_text="Как часто повторять привычку в днях. Например, 1 (ежедневно), 7 (еженедельно).",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        # Уникальность связки пользователь-действие-время-место, если нужно избежать дубликатов
        unique_together = ("owner", "action", "time", "place")

    def __str__(self):
        return f"Я, {self.owner.email}, буду {self.action} в {self.time} {self.place}"


class HabitCompletion(models.Model):
    """Модель для отслеживания выполнения привычек"""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Пользователь, выполнивший привычку",
        related_name="habit_completions",
    )
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        verbose_name="Привычка",
        help_text="Выполненная привычка",
        related_name="completions",
    )
    date_completed = models.DateField(
        default=timezone.now,  # Дата выполнения по умолчанию - текущая
        verbose_name="Дата выполнения",
        help_text="Дата, когда привычка была выполнена",
    )
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Выполнение привычки"
        verbose_name_plural = "Выполнения привычек"
        # Гарантируем, что пользователь может отметить привычку как выполненную только один раз в день.
        unique_together = ("user", "habit", "date_completed")
        # Для удобства сортировки и запросов
        ordering = ["-date_completed"]

    def __str__(self):
        return f"{self.user.email} выполнил '{self.habit.action}' {self.date_completed}"
