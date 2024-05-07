"""
Определение маршрутов для страницы профиля веб-приложения.
"""
from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user
from flask_bcrypt import check_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models import Groups_members, Groups, Users, Courses, Lessons, Tasks, Hometasks, Notifications
from app.extensions import bcrypt, db
from app.static.python.identicons import generate_avatar

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile/<id>', methods=['GET', 'POST'])
def profile(id):

    user = Users.query.filter_by(id=id).first()
    # todo: добавить страницу с ошибкой "пользователь не найден"
    if user is None:
        user = current_user

    return redirect(url_for('profile.profile_info', id=user.id))


@profile_bp.route('/profile/<id>/info', methods=['GET', 'POST'])
def profile_info(id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all())

    return render_template("profile/info.html", user=current_user, unread=unread)


@profile_bp.route('/profile/<id>/groups', methods=['GET', 'POST'])
def profile_groups(id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    groups = db.session.query(Groups).join(Groups_members).filter(Groups_members.student_id == current_user.id).all()

    result = dict.fromkeys(db.session.query(Groups).join(Groups_members).filter(Groups_members.student_id == current_user.id).all(), [])
    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all())

    for group in groups:

        result_list = []
        
        result_list.append(db.session.query(Users.id, Users.name).filter(Users.id == group.curator_id).first())
        course = db.session.query(Courses).filter(Courses.id == group.course_id).first()
        result_list.append((course.id, course.title))
        result_list.append(db.session.query(Users.id, Users.name)
                .join(Groups_members, Users.id == Groups_members.student_id)
                .filter(Groups_members.group_id == group.id)
                .all() if course.price != 0 else None)
        
        tasks = db.session.query(Tasks).join(Lessons, Lessons.id == Tasks.lesson_id).filter(Lessons.course_id == course.id).all()
        
        tasks_status = [db.session.query(Hometasks.status).filter(Hometasks.student_id == current_user.id, Hometasks.task_id == task.id).first()[0] for task in tasks]

        result_list.append(round(tasks_status.count('correct') / len(tasks) * 100, 2))
        result[group] = result_list
    
    return render_template("profile/groups.html", user=current_user, groups=result, unread=unread)


@profile_bp.route('/profile/<id>/settings', methods=['GET', 'POST'])
def profile_settings(id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all())

    return render_template("profile/settings.html", user=current_user, unread=unread)


@profile_bp.route("/profile/<id>/notifications")
def notifications(id):
    """
    Функция обработки маршрута '/profile/<id>/notifications', позволяющая просматривать уведомления пользователя.
    """
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all())
    notifications = db.session.query(Notifications).filter(Notifications.user_id == current_user.id).all()

    return render_template("profile/notifications.html", user=current_user, notifications=notifications, unread=unread)


@profile_bp.route("/profile/notification_status", methods=['POST'])
def notification_status():
    """
    Функция обработки маршрута '/profile/notification_status', позволяющая изменять статус уведомления (прочитано/не прочитано).
    """
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    try:
        data = request.get_json()

        notification_id = data.get('notificationId')
        status = data.get('status')

        db.session.query(Notifications).filter(Notifications.id == notification_id).first().unread = True if status == 'unread' else False
        db.session.commit()

        return jsonify({'category': 'success', 'message': 'Статут уведомления изменен'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)})
    

@profile_bp.route("/profile/upload_image", methods=['POST'])
def upload_image():
    """
    Функция обработки маршрута '/profile/upload_image', позволяющая загружать изображение профиля пользователя.
    """
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
    """
    Функция обработки маршрута '/profile/delete_image', позволяющая удалять изображение профиля пользователя.
    """
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    image = generate_avatar(current_user.login)
    image.save(
        f'app/static/images/users/{current_user.login}.jpg', format='jpeg')

    return jsonify({'category': 'success', 'message': 'Фото удалено'})


@profile_bp.route("/profile/update_settings", methods=['POST'])
def update_settings():
    """
    Функция обработки маршрута '/profile/update_settings', позволяющая обновлять настройки профиля пользователя.
    """
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

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
                    current_user.password = bcrypt.generate_password_hash(
                        new_password).decode('utf-8')
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
