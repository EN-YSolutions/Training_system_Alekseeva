# Личный кабинет для образовательного портала

## Инструкция по запуску на Linux

1. Установить Python (предустановлен в большинстве дистрибутивов)
2. Создание виртуального окружения (venv) и его активация

```shell
python -m venv .venv
source .venv/bin/activate
```

3. Задать преременные окружения `SECRET_KEY` и `DATABASE_URI` в командной строке, в файле `.venv/bin/activate` или напрямую в файле `config.py`

- `SECRET_KEY` - Секретный ключ, который будет использоваться для безопасной подписи cookie-файла сеанса.
- `DATABASE_URL` - Cтрока, которая сообщает SQLAlchemy, к какой базе данных подключаться.

```shell
export SECRET_KEY="..."
export DATABASE_URI="postgresql+psycopg://username:password@host:port/database_name"
```

4. Установка зависимостей в виртуальное окружение

```shell
pip install -r requirements.txt
```

5. Генерация базы данных

```shell
$ flask shell
>>> from app.extensions import db
>>> from app.models import Users, Courses, Courses_feedbacks, Groups, Groups_members, Lessons, Deadlines, Lessons_feedbacks, Tasks, Hometasks, Notifications, Users_feedbacks
>>> db.create_all()
>>> exit()
```

6. Запуск приложения

```shell
flask run
```

### Скриншоты

![Информация](assets/info.png "Информация")
