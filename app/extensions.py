"""
Файл extensions.py инициализирует необходимые расширения Flask для обеспечения функциональности веб-приложения.
"""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
db = SQLAlchemy()