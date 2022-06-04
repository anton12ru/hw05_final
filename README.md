# YaTube
## Cоциальная сеть
Описание
Социальная сеть для публикации личных дневников и постов. Пользователям предоставляется возможность создать учетную запись, опубликовать посты, подписываться на любимых авторов, комментировать и отмечать понравившиеся записи. Помимо этого, пользователю предоставляется возможность прикреплять изображения к постам, а также можно добавлять свои посты в различные группы. Например, в группу с животными можно создать пост про своего домашнего любимца и прикрепить это фотографими. Другие авторизованые пользователи могут оставлять комментарии на этот пост, ставить лайк и подписаться на автора чтобы в последующем видеть его следующие посты. 

## Технологии
- **[Python 3.9](https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe)**
- **[Django 2.2.16](https://www.djangoproject.com/download/)**
- **[CSS (bootstrap)](https://getbootstrap.su/docs/3.4/css/)**
- **[Pillow 8.3.1](https://pillow.readthedocs.io/en/stable/installation.html)**
- **[Sorl-Thumbnail 12.7.0](https://github.com/jazzband/sorl-thumbnail)**

## Инструкция по настройка и развертыванию проекта
Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone git@github.com:anton12ru/hw05_final.git
cd hw05_final
```
Создайте и активируйте виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate
```
Установите зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Выполните миграции:
```
python manage.py makemigrations
python manage.py migrate
```
Запустите проект:
```
python manage.py runserver
```
