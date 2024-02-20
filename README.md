# Личный кабинет для образовательного портала

Генерация базы данных

```shell
$ flask shell
>>> from app.extensions import db
>>> from app.models import Users, Courses, Courses_feedbacks, Groups, Groups_users, Lessons, Deadlines, Lessons_feedbacks, Progress, Tasks, Hometasks, Notifications, Users_feedbacks
>>> db.create_all()
>>> exit()
```
