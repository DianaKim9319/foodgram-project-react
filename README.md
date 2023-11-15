# Foodgram, «Продуктовый помощник».

myfoodgramjp.hopto.org

## Описание проекта:
Онлайн-сервис и API для него. 
Пользователи могут публиковать рецепты, 
подписываться на публикации других пользователей, 
добавлять понравившиеся рецепты в список «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.

## Используемые технологии:
```
Python 3.7
Django 3.2
REST Framework 3.12.4
Djoser 2.2
подробнее см. прилагаемый файл зависимостей requrements.txt
```

## Как запустить проект на удалённом сервере:
1. При необходимости, находясь на удалённом сервере, 
установите Docker, Docker Compose и Nginx,
выполнив следующие команды:

### Установка Docker
```bash
sudo apt update
```
```bash
sudo apt install curl
```
```bash
curl -fSL https://get.docker.com -o get-docker.sh
```
```bash
sudo sh ./get-docker.sh
```
### Установка Docker Compose
```bash
sudo apt-get install docker-compose-plugin 
```
### Установка Nginx
```bash
sudo apt install nginx -y 
```
```bash
sudo systemctl start nginx
```
Подготовьте файл конфигурации веб-сервера:
```bash
sudo nano /etc/nginx/sites-enabled/default
```
Заполните файл конфигурации веб-сервера:
```bash
server {
    server_name <IP_вашего_сервера> <ваш_домен>;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8000;
    }
```
После сохранения сделайте проверку синтаксиса
и перезапустите конфигурацию Nginx:
```bash
sudo nginx -t 
```
```bash
sudo systemctl reload nginx 
```
### Получение и настройка SSL-сертификата:
Установите certbot:
```bash
sudo apt install snapd 
```
```bash
sudo snap install core; sudo snap refresh core
```
```bash
sudo snap install --classic certbot
```
```bash
sudo ln -s /snap/bin/certbot /usr/bin/certbot 
```
Запустите certbot для получения SSL-сертификата:
```bash
sudo certbot --nginx
```
```bash
sudo systemctl reload nginx 
```
### Переменные окружения и секреты:
Находясь в домашней директории сервера
создайте папку проекта - foodgram.
```bash
mkdir foodgram
```
В папке foodgram создайте файл .env со следующим содержанием:
```bash
POSTGRES_DB=<имя_базы_данных>
POSTGRES_USER=<имя_пользователя>
POSTGRES_PASSWORD=<пароль_пользователя>

DB_HOST=<имя_контейнера_БД>
DB_PORT=5432

SECRET_KEY = <ваш_ключ>
```
Перейдите в настройки репозитория — Settings,
выберите Secrets and Variables →
Actions → New repository secret.
Сохраните следующие переменные:
```bash
DOCKER_PASSWORD - <имя_пользователя_на_DockerHub>
DOCKER_USERNAME - <пароль_от_DockerHub>

HOST - <IP_сервера>
USER - <username_для_подключения_к_серверу>
SSH_KEY - <приватный_SSH_ключ>
SSH_PASSPHRASE - <пароль_от_сервера>

TELEGRAM_TO - <id_вашего_телеграм_аккаунта>
TELEGRAM_TOKEN - <токен_вашего_телеграм_бота>
```
### Запуск workflow
```bash
git add .
```
```bash
git commit -m '_'
```
```bash
git push
```

## Как запустить проект локально:

Клонировать репозиторий
```bash
git clone git@github.com:DianaKim9319/foodgram-project-react.git
```

Cоздать и активировать виртуальное окружение:
```bash
cd backend
python3 -m venv venv
```

```bash
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```bash
python3 -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
python3 manage.py migrate
```

Запустить проект:

```bash
python3 manage.py runserver
```

## Примеры запросов к API:

### (POST) Регистрация пользователя
```
http://localhost:8090/api/users/
```
Пример тела запроса:
```json
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "password": "Qwerty123"
}
```
### (GET) Профиль пользователя
```
http://localhost:8090/api/users/{id}/
```
### (GET) Список ингредиентов
```
http://localhost:8090/api/ingredients/
```
### (GET) Cписок тегов
```
http://localhost:8090/api/tags/
```
### (POST) Создание рецепта
```
http://localhost:8090/api/recipes/
```
Пример тела запроса:
```json
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
### (GET) Список рецептов
```
http://localhost:8090/api/recipes/
```
### (PATCH) Обновление рецепта
```
http://localhost:8090/api/recipes/{id}/
```
Пример тела запроса:
```json
{
  "ingredients": [
    {
      "id": 839,
      "amount": 15
    }
  ],
  "tags": [
    1,
    3
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
### (POST) Добавить рецепт в список покупок
```
http://localhost:8090/api/recipes/{id}/shopping_cart/
```
Пример тела запроса:
```json
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}
```
### (POST) Добавить рецепт в избранное
```
http://localhost:8090/api/recipes/{id}/favorite/
```
Пример тела запроса:
```json
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}
```
### (POST) Подписаться на пользователя
```
http://localhost:8090/api/users/{id}/subscribe/
```
Пример тела запроса:
```json
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Имя",
  "last_name": "Фамилия",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 0,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "cooking_time": 1
    }
  ],
  "recipes_count": 0
}
```
