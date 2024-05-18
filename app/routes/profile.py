"""
Определение маршрутов для страницы профиля веб-приложения.
"""
from PIL import Image
from re import fullmatch
from datetime import datetime
from markupsafe import escape
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user
from flask_bcrypt import check_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models import Groups_members, Groups, Users, Courses, Lessons, Tasks, Hometasks, Notifications, UsersInfo, Files, FavoritesCourses
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
    
    user = Users.query.filter_by(id=id).first()
    
    user_info = UsersInfo.query.filter_by(user_id=id).first()

    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all())

    return render_template("profile/info.html", current_user=current_user, user=user, user_info=user_info, unread=unread)


@profile_bp.route('/profile/<id>/groups', methods=['GET', 'POST'])
def profile_groups(id):

    user = Users.query.filter_by(id=id).first()

    groups = db.session.query(Groups).join(Groups_members).filter(Groups_members.student_id == current_user.id, Groups.title != None).all()

    result = dict.fromkeys(groups, [])
    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all())

    for group in groups:

        result_list = []
        
        result_list.append(db.session.query(Users.id, Users.name).filter(Users.id == group.curator_id).first())
        course = db.session.query(Courses).filter(Courses.id == group.course_id).first()
        result_list.append((course.id, course.title))
        result_list.append(db.session.query(Users.id, Users.name)
                .join(Groups_members, Users.id == Groups_members.student_id)
                .filter(Groups_members.group_id == group.id)
                .all())
        
        tasks = db.session.query(Tasks).join(Lessons, Lessons.id == Tasks.lesson_id).filter(Lessons.course_id == course.id).all()
        
        tasks_status = [db.session.query(Hometasks.status).filter(Hometasks.student_id == current_user.id, Hometasks.task_id == task.id).first()[0] for task in tasks]

        result_list.append(round(tasks_status.count('correct') / len(tasks) * 100, 2))
        result[group] = result_list
    
    return render_template("profile/groups.html", current_user=current_user, user=user, groups=result, unread=unread)


@profile_bp.route('/profile/<id>/settings', methods=['GET', 'POST'])
def profile_settings(id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    user = Users.query.filter_by(id=id).first()

    if current_user.id != user.id:
        return redirect(url_for('profile.profile', id=current_user.id))

    user_info = UsersInfo.query.filter_by(user_id=current_user.id).first()

    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all())

    return render_template("profile/settings.html", current_user=current_user, user=user, user_info=user_info, unread=unread)


@profile_bp.route('/profile/<id>/courses', methods=['GET'])
def profile_courses(id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    user = Users.query.filter_by(id=id).first()
    # todo: добавить страницу с ошибкой "пользователь не найден"
    if user is None:
        user = current_user

    return redirect(url_for('profile.courses_taken', id=user.id))


@profile_bp.route('/profile/<id>/courses/taken', methods=['GET'])
def courses_taken(id):

    user = Users.query.filter_by(id=id).first()

    groups = db.session.query(Groups).join(Groups_members).filter(Groups_members.student_id == user.id).all()

    result = dict.fromkeys(groups, [])
    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all())

    for group in groups:

        result_list = []
        
        course = db.session.query(Courses).filter(Courses.id == group.course_id).first()
        result_list.append((course.id, course.title, course.description))
        
        tasks = db.session.query(Tasks).join(Lessons, Lessons.id == Tasks.lesson_id).filter(Lessons.course_id == course.id).all()

        tasks_status = [db.session.query(Hometasks.status).filter(Hometasks.student_id == user.id, Hometasks.task_id == task.id).first() for task in tasks]
        tasks_status = [status[0] if status else "pending" for status in tasks_status]        

        result_list.append(round(tasks_status.count('correct') / len(tasks) * 100, 2))
        result[group] = result_list

    return render_template("profile/courses_taken.html", current_user=current_user, user=user, groups=result, unread=unread)


@profile_bp.route('/profile/<id>/courses/favorites', methods=['GET'])
def courses_favorites(id):
    
    user = Users.query.filter_by(id=id).first()
    
    courses = db.session.query(Courses).join(FavoritesCourses).filter(FavoritesCourses.user_id == id).all()

    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all())

    return render_template("profile/courses_favorites.html", current_user=current_user, user=user, courses=courses, unread=unread)


@profile_bp.route("/profile/favorite_toggle", methods=['POST', 'DELETE'])
def favorite_toggle():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    try:

        data = request.get_json()
        course_id = data.get('course_id')

        if request.method == 'POST':
            
            new_fav_course = FavoritesCourses(
                course_id=course_id,
                user_id=current_user.id
            )

            db.session.add(new_fav_course)
            db.session.commit()

            return jsonify({'category': 'success', 'message': 'Курс добавлен в избранные'})
        
        elif request.method == 'DELETE':
        
            FavoritesCourses.query.filter(FavoritesCourses.course_id == course_id, FavoritesCourses.user_id == current_user.id).delete()
            db.session.commit()

            return jsonify({'category': 'success', 'message': 'Курс удален из избранных'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)})


@profile_bp.route("/profile/send_request", methods=["POST"])
def send_request():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    try:

        data = request.get_json()
        course_id = data.get('course_id')
        group_id = data.get('group_id')
        message_text = escape(data.get('message_text'))
        data_type = data.get('data_type')

        group = Groups.query.filter_by(id = group_id).first()

        # todo: заменить на placeholder группы
        group_link = f'<a href="{url_for('profile.profile_info', id=current_user.id)}">{group.title}</a>'
        user_link = f'<a href="{url_for('profile.profile_info', id=current_user.id)}">{current_user.name}</a>'

        if data_type == "adviceModal":
            title = "Запрос консультации"
            notification_text = f'Пользователь {user_link} из группы {group_link} запрашивает консультацию. <br /> Текст сообщения: {message_text}'
        elif data_type == "individualModal":
            title = "Запрос индивидуального графика"
            notification_text = f'Пользователь {user_link} из группы {group_link} запрашивает индивидуальный график обучения. <br /> Текст сообщения {message_text}'

        new_notify = Notifications(
            user_id=group.curator_id,
            title=title,
            description=notification_text,
            date=datetime.now()
        )

        db.session.add(new_notify)
        db.session.commit()

        return jsonify({'category': 'success', 'message': 'Запрос отправлен'})
        

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)})


@profile_bp.route("/profile/<id>/notifications")
def notifications(id):
    """
    Функция обработки маршрута '/profile/<id>/notifications', позволяющая просматривать уведомления пользователя.
    """
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    unread = len(db.session.query(Notifications).filter(Notifications.user_id == current_user.id, Notifications.unread == True).all())
    notifications = db.session.query(Notifications).filter(Notifications.user_id == current_user.id).all()

    return render_template("profile/notifications.html", current_user=current_user, notifications=notifications, unread=unread)


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
    email_regex = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'

    try:
        new_name = request.form.get('new-name')
        scoring_system = int(request.form.get('scoring-system'))
        old_password = request.form.get('old-password')
        new_password = request.form.get('new-password')
        confirm_password = request.form.get('confirm-password')
        email = request.form.get('new-email')
        date = request.form.get('new-date')
        address = request.form.get('new-address')
        phone = request.form.get('new-phone')

        # todo: перенести в регистрацию       
        current_user_info = UsersInfo.query.filter_by(user_id = current_user.id).first()
        if not current_user_info:
            current_user_info = UsersInfo(user_id = current_user.id)
            db.session.add(current_user_info)
            db.session.commit()

        if new_name and new_name != current_user.name:
            current_user.name = new_name

        if scoring_system_names.get(scoring_system, 'points') != current_user.scoring_system:
            current_user.scoring_system = scoring_system_names[scoring_system]

        if not fullmatch(email_regex, email):
            return jsonify({'category': 'warning', 'message': 'Почта скорей всего не валидна. Обратитесь к администратору.'})
        elif email != current_user_info.email:
            current_user_info.email = email

        if date != str(current_user_info.birth_date):
            current_user_info.birth_date = date

        if address != current_user_info.home_address:
            current_user_info.home_address = address

        if phone != current_user_info.phone_number:
            current_user_info.phone_number = phone

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
