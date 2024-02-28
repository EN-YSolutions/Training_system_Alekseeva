from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_bcrypt import check_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.forms import SettingsForm
from app.extensions import bcrypt, db

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
def profile():
    menu_type = request.args.get('menu')

    settings = SettingsForm()
    settings.scoring_system.choices = [(1, 'Абстрактная'), (2, 'Числовые значения')]

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
                    current_user.password = bcrypt.generate_password_hash(new_password)
                
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
