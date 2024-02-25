from flask import Blueprint, render_template, request
from flask_login import current_user

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
def profile():
    menu_type = request.args.get('menu')

    return render_template("profile/profile.html", user=current_user, menu_type=menu_type)
