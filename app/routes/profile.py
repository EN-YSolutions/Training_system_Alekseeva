from flask import Blueprint, render_template
from flask_login import current_user

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/')
def profile():
    return render_template("profile/profile.html", user=current_user)
