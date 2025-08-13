from celery import shared_task
from django.utils import timezone

from habits.models import Habit
from habits.services import send_telegram_message


@shared_task
def send_start_habit():
    """Отправляет напоминание Пользователю, что пора выполнять полезную привычку"""

    now = timezone.now()
    now_moscow = now.astimezone(timezone.get_current_timezone())
    # Получаем все привычки, у которых время совпадает с текущим.
    habits_to_remind = Habit.objects.filter(
        is_pleasant=False, time__hour=now_moscow.hour, time__minute=now_moscow.minute
    ).exclude(owner__tg_chat_id=None)

    for habit in habits_to_remind:
        habit_owner = habit.owner
        if habit_owner and habit_owner.tg_chat_id:
            try:
                message = str(habit)
                send_telegram_message(chat_id=habit_owner.tg_chat_id, message=message)
                print(f"Отправлено напоминание пользователю {habit_owner.tg_chat_id} для привычки: {habit.action}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {habit_owner.tg_chat_id}: {e}")
