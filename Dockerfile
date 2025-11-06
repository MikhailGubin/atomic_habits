# Указываем базовый образ
FROM python:3.13-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файл с зависимостями
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем остальные файлы проекта в контейнер
COPY . .

# Открываем порт 8000 для взаимодействия с приложением
EXPOSE 8000

#Создаю директорию для статических файлов
RUN mkdir -p /app/static /app/staticfiles

# Создаем директорию для медиафайлов
RUN mkdir -p /app/media

# Определяем команду для запуска приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#Команда для сборки образа:
#docker build -t atomic_habits .
#Команда для запуска:
#docker run -d --name atomic_habits -p 8000:8000 -v my-media-volume:/app/media -e DEBUG=1 atomic_habits