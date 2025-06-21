# Базовый образ Python с уже установленными зависимостями
FROM python:3.9-slim

# Установим рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y libssl-dev libffi-dev gcc
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем бота
CMD ["python", "bot.py"]