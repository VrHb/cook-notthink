# Сервис рекомендаций блюд

## Запуск:

### 1. Копируем содержимое проекта себе в рабочую директорию
```
git clone <метод копирования>
```

### 2. Разворачиваем внутри скопированного проекта виртуальное окружение:
```
python -m venv <название виртуального окружения>
```

### 3. Устанавливаем библиотеки:
```
pip install -r requirements.txt
```

### 4. Для хранения переменных окружения создаем файл .env:
```
touch .env
```
Доступны три переменные:

* SECRET_KEY
Генерируем секретный ключ DJANGO в интерактивном режиме python:
    1. `python`
    2. `import django`
    3. `from django.core.management.utils import get_random_secret_key`
    4. `print(get_random_secret_key())`
    5. Копируем строку в `.env` файл: `DJANGO_KEY='ваш ключ'`    
    6. Для тестирования бота добавляем токен в `.env` файл: `BOT_TOKEN='токен вашего бота'`

* TELEGRAM_TOKEN
Можно получить через BotFather

* DEBUG
Можно установить True или False

### 5. Переходим в директорию проекта и выполняем миграции в ДБ: 
```
python manage.py makemigrations db; python manage.py migrate
```
#### Важно: 
Выполнять этот шаг нужно при изменении models.py

### 6. Запускаем модуль бота:
Сам модуль находится в директории foodplan/management/commands
```
python manage.py bot
```
Если ответил на сообщение, значит все ок
