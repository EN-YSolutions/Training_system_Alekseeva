"""
Определение маршрута для главной страницы веб-приложения.
"""
from flask import Blueprint, render_template
from flask_login import current_user
from app.models import Notifications
from app.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Функция обработки маршрута '/', отображающая главную страницу приложения.
    Происходит подсчет количества непрочитанных уведомлений для текущего пользователя, 
    если он аутентифицирован.
    """
    
    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all()) if current_user.is_authenticated else 0

    return render_template("main/index.html", user=current_user, unread=unread)
