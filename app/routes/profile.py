from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import current_user
from flask_bcrypt import check_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from PIL import Image
from app.forms import SettingsForm
from app.extensions import bcrypt, db
from app.static.python.identicons import generate_avatar

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    menu_type = request.args.get('menu')

    return render_template("profile/profile.html", user=current_user, menu_type=menu_type)


@profile_bp.route("/profile/upload_image", methods=['POST'])
def upload_image():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if 'image' not in request.files:
        return jsonify({'category': 'danger', 'message': 'Нет файла с изображением'})

    file = request.files['image']

    if file:
        image = Image.open(file.stream)

        min_side = min(image.width, image.height)

        left = (image.width - min_side) / 2
        top = (image.height - min_side) / 2
        right = (image.width + min_side) / 2
        bottom = (image.height + min_side) / 2

        image = image.crop((left, top, right, bottom))

        image = image.resize((150, 150), Image.LANCZOS)

        if image.mode != 'RGB':
            image = image.convert('RGB')

        image.save(
            f'app/static/images/users/{current_user.login}.jpg', format="JPEG")

        return jsonify({'category': 'success', 'message': 'Фото отправлено'})

    else:

        return jsonify({'category': 'danger', 'message': 'Ошибка на сервере'})


@profile_bp.route("/profile/delete_image", methods=['DELETE'])
def delete_image():

    image = generate_avatar(current_user.login)
    image.save(
        f'app/static/images/users/{current_user.login}.jpg', format='jpeg')

    return jsonify({'category': 'success', 'message': 'Фото удалено'})


@profile_bp.route("/profile/update_settings", methods=['POST'])
def update_settings():

    scoring_system_names = {1: 'abstract', 2: 'points'}

    try:
        new_name = request.form.get('new-name')
        scoring_system = int(request.form.get('scoring-system'))
        old_password = request.form.get('old-password')
        new_password = request.form.get('new-password')
        confirm_password = request.form.get('confirm-password')

        if new_name and new_name != current_user.name:
            current_user.name = new_name

        if scoring_system_names.get(scoring_system, 'points') != current_user.scoring_system:
            current_user.scoring_system = scoring_system_names[scoring_system]

        if old_password:
            if check_password_hash(current_user.password, old_password):
                if new_password == confirm_password:
                    current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                else:
                    return jsonify({'category': 'warning', 'message': 'Пароли не совпадают'})
            else:
                return jsonify({'category': 'warning', 'message': 'Ошибка в старом пароле'})

        db.session.commit()

        return jsonify({'category': 'success', 'message': 'Настройки сохранены'})

    except IntegrityError as e:
        db.session.rollback()
        print(str(e))
        return jsonify({'category': 'danger', 'message': 'Ошибка на сервере'})

    except SQLAlchemyError as e:
        db.session.rollback()
        print(str(e))
        return jsonify({'category': 'danger', 'message': 'Ошибка на сервере'})

    return jsonify({'category': 'danger', 'message': 'Ошибка на сервере'})
