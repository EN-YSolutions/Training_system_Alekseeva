"""
Файл models.py содержит описания классов моделей для работы с базой данных. 
Каждый класс содержит описание полей таблицы и их взаимосвязей с другими таблицами. 
Также предоставлены методы __repr__ для отображения объектов в виде строк.
"""

from flask_login import UserMixin
from sqlalchemy import func
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import String, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, NUMERIC, DATE
from app.extensions import db


class Users(UserMixin, db.Model):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True, unique=True, server_default=func.gen_random_uuid())
    login = Column(String(32), unique=True, nullable=False)
    password = Column(String(60), unique=False, nullable=False)
    role = Column(Enum("admin", "curator", "teacher", "student", name="user_role"), unique=False, nullable=False)
    name = Column(String(255), unique=False, nullable=False)
    balance = Column(NUMERIC(19, 2), unique=False, nullable=False)
    scoring_system = Column(Enum("abstract", "points", name="score_type"), unique=False, nullable=False)

    users_info = relationship("UsersInfo", backref="user", lazy=True)
    courses = relationship("Courses", backref="author", lazy=True)
    courses_feedbacks = relationship("Courses_feedbacks", backref="author", lazy=True)
    groups = relationship("Groups", backref="curator", lazy=True)
    groups_members = relationship("Groups_members", backref="student", lazy=True)
    lessons = relationship("Lessons", backref="teacher", lazy=True)
    lessons_feedbacks = relationship("Lessons_feedbacks", backref="author", lazy=True)
    hometasks = relationship("Hometasks", backref="student", lazy=True)
    notifications = relationship("Notifications", backref="user", lazy=True)
    users_feedbacks = relationship("Users_feedbacks", backref="user", lazy=True, foreign_keys="[Users_feedbacks.user_id]")
    users_feedbacks_2 = relationship("Users_feedbacks", backref="author", lazy=True, foreign_keys="[Users_feedbacks.author_id]")

    def __repr__(self):
        return '<User: %r>' % self.id
    

class UsersInfo(db.Model):
    _tablename_ = 'users_info'

    user_id = Column(UUID, ForeignKey("users.id"), primary_key=True, unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    birth_date = Column(DATE, unique=False, nullable=True)
    home_address = Column(String(511), unique=False, nullable=True)
    phone_number = Column(String(32), unique=False, nullable=True)

    def __repr__(self):
        return '<UsersInfo: %r' % self.user_if


class Courses(db.Model):
    __tablename__ = 'courses'

    id = Column(UUID, primary_key=True, unique=True, server_default=func.gen_random_uuid())
    author_id = Column(UUID, ForeignKey("users.id"), nullable=False, unique=False)
    price = Column(NUMERIC(19, 2), unique=False, nullable=False)
    title = Column(String(255), unique=False, nullable=False)
    description = Column(Text, unique=False, nullable=True)

    courses_feedbacks = relationship("Courses_feedbacks", backref="course", lazy=True)
    groups = relationship("Groups", backref="course", lazy=True)
    lessons = relationship("Lessons", backref="course", lazy=True)

    def __repr__(self):
        return '<Course: %r>' % self.id


class FavoritesCourses(db.Model):
    __tablename__ = 'favorites_courses'

    course_id = Column(UUID, ForeignKey("courses.id"), primary_key=True, nullable=False, unique=False)
    user_id = Column(UUID, ForeignKey("users.id"), primary_key=True, nullable=False, unique=False)

    def __repr__(self):
        return "<FavoritesCourses: %s - %s>" % self.course_id, self.user_id


class Courses_feedbacks(db.Model):
    __tablename__ = 'courses_feedbacks'

    id = Column(UUID, primary_key=True, unique=True, server_default=func.gen_random_uuid())
    course_id = Column(UUID, ForeignKey("courses.id"), nullable=False, unique=False)
    author_id = Column(UUID, ForeignKey("users.id"), nullable=False, unique=False)
    text = Column(Text, nullable=False, unique=False)
    date = Column(TIMESTAMP(timezone=True), nullable=False, unique=False)

    def __repr__(self):
        return '<Courses_feedback: %r>' % self.id
    


class Groups(db.Model):
    __tablename__ = 'groups'

    id = Column(UUID, primary_key=True, unique=True, server_default=func.gen_random_uuid())
    course_id = Column(UUID, ForeignKey("courses.id"), nullable=False, unique=False)
    curator_id = Column(UUID, ForeignKey("users.id"), nullable=True, unique=False)
    title = Column(String(255), unique=False, nullable=True)

    deadlines = relationship("Deadlines", backref="group", lazy=True)
    groups_members = relationship("Groups_members", backref="group", lazy=True)

    def __repr__(self):
        return "<Group: %s>" % self.id
    

class Groups_members(db.Model):
    __tablename__ = 'groups_members'

    group_id = Column(UUID, ForeignKey("groups.id"), primary_key=True, nullable=False, unique=False)
    student_id = Column(UUID, ForeignKey("users.id"), primary_key=True, nullable=False, unique=False)

    def __repr__(self):
        return "<Groups_users: %s - %s>" % (self.group_id, self.student_id)
    

class Lessons(db.Model):
    __tablename__ = 'lessons'

    id = Column(UUID, primary_key=True, unique=True, server_default=func.gen_random_uuid())
    course_id = Column(UUID, ForeignKey("courses.id"), nullable=False, unique=False)
    teacher_id = Column(UUID, ForeignKey("users.id"), nullable=False, unique=False)
    title = Column(String(255), nullable=False, unique=False)
    text = Column(Text, nullable=False, unique=False)

    deadlines = relationship("Deadlines", backref="lesson", lazy=True)
    lessons_feedbacks = relationship("Lessons_feedbacks", backref="lesson", lazy=True)
    tasks = relationship("Tasks", backref="lesson", lazy=True)
    file = relationship("Files", backref="lesson", lazy=True)

    def __repr__(self):
        return '<Lesson: %s>' % self.id 


class Deadlines(db.Model):
    __tablename__ = 'deadlines'

    group_id = Column(UUID, ForeignKey("groups.id"), primary_key=True, nullable=False, unique=False)
    lesson_id = Column(UUID, ForeignKey("lessons.id"), primary_key=True, nullable=False, unique=False)
    deadline = Column(TIMESTAMP(timezone=True), nullable=False, unique=False)

    def __repr__(self):
        return '<Deadline: %s - %s>' % (self.group_id, self.lesson_id)


class Lessons_feedbacks(db.Model):
    __tablename__ = 'lessons_feedbacks'

    id = Column(UUID, primary_key=True, unique=True, server_default=func.gen_random_uuid())
    lesson_id = Column(UUID, ForeignKey("lessons.id"), nullable=False, unique=False)
    author_id = Column(UUID, ForeignKey("users.id"), nullable=False, unique=False)
    text = Column(Text, nullable=False, unique=False)
    date = Column(TIMESTAMP(timezone=True), nullable=False, unique=False)

    def __repr__(self):
        return '<Courses_feedback: %r>' % self.id
    

class Tasks(db.Model):
    __tablename__ = 'tasks'

    id = Column(UUID, primary_key=True, unique=True, server_default=func.gen_random_uuid())
    lesson_id = Column(UUID, ForeignKey("lessons.id"), nullable=False, unique=False)
    title = Column(String(255), nullable=False, unique=False)
    description = Column(Text, nullable=False, unique=False)

    hometasks = relationship("Hometasks", backref="task", lazy=True)
    file = relationship("Files", backref="task", lazy=True)

    def __repr__(self):
        return '<Task: %s>' % self.id 
    

class Hometasks(db.Model):
    __tablename__ = 'hometasks'

    id = Column(UUID, primary_key=True, unique=True, server_default=func.gen_random_uuid())
    task_id = Column(UUID, ForeignKey("tasks.id"), nullable=False, unique=False)
    student_id = Column(UUID, ForeignKey("users.id"), nullable=False, unique=False)
    title = Column(String(255), nullable=False, unique=False)
    text = Column(Text, nullable=False, unique=False)
    status = Column(Enum("pending", "needs revision", "correct", "incorrect", name = "task_status"), nullable=False, unique=False)

    __table_args__ = (UniqueConstraint(task_id, student_id),)

    file = relationship("Files", backref="hometask", lazy=True)

    def __repr__(self):
        return '<Hometask: %s>' % self.id 


class Files(db.Model):
    __tablename__ = 'files'

    id = Column(UUID, primary_key=True, unique=True, server_default=func.get_random_uuid())
    name = Column(String(255), nullable=False, unique=False)
    lesson_id = Column(UUID, ForeignKey("lessons.id"), nullable=True, unique=False)
    task_id = Column(UUID, ForeignKey("tasks.id"), nullable=True, unique=False)
    hometask_id = Column(UUID, ForeignKey("hometasks.id"), nullable=True, unique=False)

    def __repr__(self):
        return '<File: %s>' % self.id 


class Notifications(db.Model):
    __tablename__ = 'notifications'

    id = Column(UUID, primary_key=True, unique=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, unique=False)
    title = Column(String(255), nullable=False, unique=False)
    description = Column(Text, nullable=False, unique=False)
    unread = Column(Boolean, nullable=False, unique=False, default=True)
    date = Column(TIMESTAMP(timezone=True), nullable=False, unique=False)

    def __repr__(self):
        return '<Notification: %s>' % self.id 


class Users_feedbacks(db.Model):
    __tablename__ = 'users_feedbacks'

    id = Column(UUID, primary_key=True, nullable=False, unique=False, server_default=func.gen_random_uuid())
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, unique=False)
    author_id = Column(UUID, ForeignKey("users.id"), nullable=False, unique=False)
    text = Column(Text, nullable=False, unique=False)
    date = Column(TIMESTAMP(timezone=True), nullable=False, unique=False)

    def __repr__(self):
        return '<Users_feedback: %s>' % self.id 