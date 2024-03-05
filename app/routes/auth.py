from os.path import isfile
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, logout_user, login_user
from flask_bcrypt import check_password_hash
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.types import Numeric
from app.forms import LoginForm, RegisterForm 
from app.models import Users
from app.extensions import db, bcrypt
from app.static.python.identicons import generate_avatar

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = Users.query.filter_by(login=form.login.data).first()
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                if not isfile(f"app/static/images/users/{current_user.login}.jpg"):
                    image = generate_avatar(current_user.login)
                    image.save(f'app/static/images/users/{current_user.login}.jpg', format='jpeg')
                return redirect(url_for('main.index'))
            else:
                flash("Ошибка пароля", "danger")
        
        except AttributeError as e:
            print(str(e))
            flash("Ошибка в логине пользователя", "danger")

        except IntegrityError as e:
            db.session.rollback() 
            print(str(e))
            flash("Ошибка при входе в аккаунт", "danger")
        
        except SQLAlchemyError as e:
            db.session.rollback() 
            print(str(e))

    return render_template('auth/login.html', user=current_user, form=form)


@auth_bp.route('/register', methods=['POST', 'GET'])
def register():

    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user_name = form.user_name.data 
            user_login = form.user_login.data 
            user_password = form.user_password.data
            
            newuser = Users(
                name=user_name,
                login=user_login,
                password = bcrypt.generate_password_hash(user_password).decode('utf-8'),
                role="student",
                balance=func.cast(0.0, Numeric(precision=10, scale=2)),
                scoring_system="points",
            )
    
            db.session.add(newuser)
            db.session.commit()

            image = generate_avatar(newuser.login)
            image.save(f'app/static/images/users/{newuser.login}.jpg', format='jpeg')

            flash(f"Аккаунт успешно создан", "success")

            return redirect(url_for("auth.login"))

        except IntegrityError as e:
            db.session.rollback() 
            print(str(e))
            flash("Ошибка при регистрации аккаунта", "danger")
        
        except SQLAlchemyError as e:
            db.session.rollback() 
            print(str(e))

    return render_template('auth/register.html', user=current_user, form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
