# Личный кабинет для образовательного портала

### Генерация базы данных

```shell
$ flask shell
>>> from app.extensions import db
>>> from app.models import Users, Courses, Courses_feedbacks, Groups, Groups_members, Lessons, Deadlines, Lessons_feedbacks, Tasks, Hometasks, Notifications, Users_feedbacks
>>> db.create_all()
>>> exit()
```

### Запуск приложения

Необходимо установить переменные окружения `SECRET_KEY` и `DATABASE_URI`.
Запуск приложения осуществляется следующей командой.

```shell
flask run
```
