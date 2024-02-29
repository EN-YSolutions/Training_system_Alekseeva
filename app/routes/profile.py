from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user
from flask_bcrypt import check_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from PIL import Image
from app.forms import SettingsForm
from app.extensions import bcrypt, db
from app.static.python.identicons import generate_avatar

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    menu_type = request.args.get('menu')

    settings = SettingsForm()
    settings.scoring_system.choices = [
        (1, 'Абстрактная'), (2, 'Числовые значения')]

    scoring_system_names = {1: 'abstract', 2: 'points'}

    if request.method == 'POST':
        if settings.validate_on_submit():
            try:
                user_name = settings.user_name.data
                old_password = settings.old_password.data
                new_password = settings.new_password.data
                confirm_password = settings.confirm_password.data
                scoring_system = settings.scoring_system.data

                if user_name != current_user.name:
                    current_user.name = user_name

                if check_password_hash(current_user.password, old_password):
                    current_user.password = bcrypt.generate_password_hash(
                        new_password)

                if scoring_system_names[scoring_system] != current_user.scoring_system:
                    current_user.scoring_system = scoring_system_names[scoring_system]

                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                print(str(e))

            except SQLAlchemyError as e:
                db.session.rollback()
                print(str(e))

    return render_template("profile/profile.html", user=current_user, menu_type=menu_type, settings_form=settings)


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

        image.save(f'app/static/images/users/{current_user.login}.jpg', format="JPEG")

        return jsonify({'category': 'success', 'message': 'Фото отправлено'})
    
    else:

        return jsonify({'category': 'danger', 'message': 'Ошибка на сервере'})
    

@profile_bp.route("/profile/delete_image", methods=['DELETE'])
def delete_image():
    
    image = generate_avatar(current_user.login)
    image.save(f'app/static/images/users/{current_user.login}.jpg', format='jpeg')

    return jsonify({'category': 'success', 'message': 'Фото удалено'})