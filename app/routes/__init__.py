# Импорт Blueprint'ов
from .main import main_bp
from .auth import auth_bp
from .profile import profile_bp

# Возвращает Blueprint'ы
def get_blueprints():
    return (main_bp, auth_bp, profile_bp)