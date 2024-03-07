"""
Файл extensions.py инициализирует необходимые расширения Flask для обеспечения функциональности веб-приложения.
"""
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

# Управление аутентификацией пользователей
login_manager = LoginManager()
# Хэширование паролей пользователей
bcrypt = Bcrypt()
# Взаимодействие с базой данных в объектно-ориентированном стиле
db = SQLAlchemy()