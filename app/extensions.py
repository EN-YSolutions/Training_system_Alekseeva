from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

login_manager = LoginManager()
bcrypt = Bcrypt()
db = SQLAlchemy()