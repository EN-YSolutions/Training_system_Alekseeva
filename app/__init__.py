from flask import Flask
from app.routes import get_blueprints
from config import Config
from app.extensions import login_manager, bcrypt, db
from app.models import Users
from uuid import UUID


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    login_manager.session_protection = "strong"
    login_manager.login_view = "login"
    login_manager.login_message_category = "info"

    login_manager.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)


    for blueprint in get_blueprints():
        app.register_blueprint(blueprint)

    return app


@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = UUID(user_id)
    except ValueError:
        return None
    
    return Users.query.filter_by(id=user_id).first()
