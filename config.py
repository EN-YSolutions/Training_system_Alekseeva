"""
Файл config.py содержит класс конфигурации Flask-приложения.
"""
import os


class Config:
    """
    - SECRET_KEY: Секретный ключ, используемый Flask для подписи данных, таких как сессии и токены.
    - SQLALCHEMY_DATABASE_URI: URI базы данных, используемой SQLAlchemy для подключения к базе данных. 
    """
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
