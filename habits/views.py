from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from habits.models import Habit
from habits.pagination import CustomPagination
from habits.serializer import HabitSerializer
from users.permissions import IsOwner


class HabitCreateAPIView(CreateAPIView):
    """Создаёт объект класса 'Привычка'"""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = IsAuthenticated

    def perform_create(self, serializer):
        """Добавляет текущего пользователя в поле "Владелец" модели "Привычка" """
        serializer.save(owner=self.request.user)


class HabitOwnerListAPIView(ListAPIView):
    """Передаёт список привычек текущего Пользователя с пагинацией"""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Habit.objects.filter(owner=user)
        else:
            return Habit.objects.none()


class PublicHabitListAPIView(ListAPIView):
    """Передаёт список публичных привычек"""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Habit.objects.filter(is_public=True)
        else:
            return Habit.objects.none()


class HabitRetrieveAPIView(RetrieveAPIView):
    """Передаёт представление определённого объекта класса 'Привычка'"""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = (IsAuthenticated, IsOwner)


class HabitUpdateAPIView(UpdateAPIView):
    """Меняет информацию в представлении объекта класса 'Привычка'"""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = (
        IsAuthenticated,
        IsOwner,
    )


class HabitDestroyAPIView(DestroyAPIView):
    """Удаляет объект класса 'Привычка'"""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = (IsAuthenticated, IsOwner)
