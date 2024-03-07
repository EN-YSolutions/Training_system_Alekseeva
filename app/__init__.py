"""
Конфигурация Flask-приложения и его инициализация.
"""
from os import makedirs
from uuid import UUID
from flask import Flask
from config import Config
from app.routes import get_blueprints
from app.extensions import login_manager, bcrypt, db
from app.models import Users


def create_app(config_class=Config) -> Flask:
    """
    Cоздает экземпляр Flask-приложения, настраивает его с помощью переданного класса конфигурации,
    и инициализирует расширения LoginManager, Bcrypt и SQLAlchemy.
    """

    makedirs("app/static/images", exist_ok=True)
    makedirs("app/static/images/users", exist_ok=True)

    app = Flask(__name__)
    app.config.from_object(config_class)

    login_manager.session_protection = "strong"
    login_manager.login_view = "login"
    login_manager.login_message_category = "info"

    login_manager.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)

    # Регистрирацая всех маршрутов
    for blueprint in get_blueprints():
        app.register_blueprint(blueprint)

    return app


@login_manager.user_loader
def load_user(user_id) -> Users:
    """
    Загрузка пользователя на основе его идентификатора с использованием модуля flask_login.
    """
    try:
        user_id = UUID(user_id)
    except ValueError:
        return None
    
    return Users.query.filter_by(id=user_id).first()
