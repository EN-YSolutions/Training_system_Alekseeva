from os.path import isfile
import bcrypt
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, logout_user, login_user
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.types import Numeric
from app.models import Users
from app.extensions import db
from app.static.python.identicons import generate_avatar

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        login_data = request.form.get('login')
        password_data = request.form.get('password')

        try:
            user = Users.query.filter_by(login=login_data).first()

            if not user:
                return jsonify({'category': 'warning', 'message': 'Ошибка в логине пользователя'})
            
            if user and bcrypt.checkpw(password_data.encode('utf-8'), user.password.encode('utf-8')):
                login_user(user)
                if not isfile(f"app/static/images/users/{current_user.login}.jpg"):
                    image = generate_avatar(current_user.login)
                    image.save(f'app/static/images/users/{current_user.login}.jpg', format='jpeg')
                return jsonify({'category': 'success', 'message': 'Успешный вход', 'redirect_url': url_for('profile.profile', id=user.id)})
            else:
                return jsonify({'category': 'warning', 'message': 'Ошибка пароля'})
        
        except IntegrityError as e:
            db.session.rollback() 
            print(str(e))
            return jsonify({'category': 'danger', 'message': 'Ошибка при входе в аккаунт'})
        
        except SQLAlchemyError as e:
            db.session.rollback() 
            print(str(e))
            return jsonify({'category': 'danger', 'message': 'Ошибка на сервере'})

    return render_template('auth/login.html', current_user=current_user)


@auth_bp.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        try:
            user_name = request.form.get('name')
            user_login = request.form.get('login')
            user_password = request.form.get('password')
            user_cpassword = request.form.get('cpassword')

            if user_password != user_cpassword:
                return jsonify({'category': 'warning', 'message': 'Пароли не совпадают'})
            
            if Users.query.filter_by(login=user_login).first():
                return jsonify({'category': 'warning', 'message': 'Пользователь с таким логином уже существует'})
            
            newuser = Users(
                name=user_name,
                login=user_login,
                password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                role="student",
                balance=func.cast(0.0, Numeric(precision=10, scale=2)),
                scoring_system="points",
            )

            db.session.add(newuser)
            db.session.commit()

            image = generate_avatar(newuser.login)
            image.save(f'app/static/images/users/{newuser.login}.jpg', format='jpeg')

            login_user(newuser)

            return jsonify({'category': 'success', 'message': 'Пользователь создан', 'redirect_url': url_for('profile.profile', id=newuser.id)})
        
        except IntegrityError as e:
            db.session.rollback() 
            print(str(e))
            return jsonify({'category': 'danger', 'message': 'Ошибка при создании аккаунта'})
        
        except SQLAlchemyError as e:
            db.session.rollback() 
            print(str(e))
            return jsonify({'category': 'danger', 'message': 'Ошибка на сервере'})

    return render_template('auth/register.html', current_user=current_user)


@auth_bp.route('/logout')
def logout():
    """
    Функция обработки маршрута /logout, выполняющая выход пользователя из системы.
    """
    logout_user()
    return redirect(url_for('auth.login'))
