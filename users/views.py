from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny

from users.models import User
from users.serializer import UserSerializer


class UserCreateAPIView(CreateAPIView):
    """Контроллер для регистрации пользователей"""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.is_active = True
        user.save()


class UserListAPIView(ListAPIView):
    """Передаёт представления объектов класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveAPIView(RetrieveAPIView):
    """Передаёт представление определённого объекта класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdateAPIView(UpdateAPIView):
    """Меняет информацию в представлении объекта класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDestroyAPIView(DestroyAPIView):
    """Удаляет объект класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
