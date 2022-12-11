Проект является продолжением рание опубликованного проекта YaTube.
Данный проект реализован на API, что облегчит интеграцию с мобильными приложениями.

Развертывание проекта:

Клонировать репозиторий на компьютер/сервер.

    git clone ....

Создать и запустить виртуальное окружение.

    Windows:
        python -m venv venv
        source venv/Scripts/activate

    Linux:
        python3 -m venv env
        source env/bin/activate
        python3 -m pip install --upgrade pip

Установить зависимости из файла requirements.txt.

    pip install -r requirements.txt

Установить миграции.

    python manage.py migrate

В файле settings.py прописать используемый домен.

    ALLOWED_HOSTS = ['список используемых доменов']

Запустить проект.

    python3 manage.py runserver


Документация по проекту доступна:

    http://127.0.0.1:8000/redoc/
