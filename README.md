### Платформа с рецептами

Сайт, на котором пользователи могут 
публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Пользователям сайта также будет доступен сервис «Список покупок». 
Он позволит создавать список продуктов, 
которые нужно купить для приготовления выбранных блюд.

```commandline
Реализован backend, API, задеплоен на сервер в контейнерах: 
nginx, PostgreSQL и Django через docker-compose 
```
### Запуск проекта в dev-режиме (только бэк):

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/jisdtn/food-app-project
```

```
cd food-app-project
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
cd backend
```

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить backend проекта:

```
python3 manage.py runserver
```
### Примеры запросов к API.

```commandline
http://localhost/api/users/ ('GET')
```
```commandline
http://localhost/api/recipes/{id}/ ('GET')
```
```commandline
http://localhost/api/recipes/download_shopping_cart/ ('GET')
```
```commandline
http://localhost/api/users/subscriptions/ ('GET')
```
