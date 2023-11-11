# Foodgram, «Продуктовый помощник».

myfoodgramjp.hopto.org

## Описание проекта:
Онлайн-сервис и API для него. 
Пользователи могут публиковать рецепты, 
подписываться на публикации других пользователей, 
добавлять понравившиеся рецепты в список «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.


## Как запустить проект:

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
## Используемые технологии:
```
Python 3.7
Django 3.2
REST Framework 3.12.4
Djoser 2.2
подробнее см. прилагаемый файл зависимостей requrements.txt
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
