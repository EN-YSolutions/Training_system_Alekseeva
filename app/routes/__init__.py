# Импорт Blueprint'ов
from flask import Blueprint
from .main import main_bp
from .auth import auth_bp
from .profile import profile_bp

# Возвращает список Blueprint'ов
def get_blueprints() -> list[Blueprint]:

    return (main_bp, auth_bp, profile_bp)