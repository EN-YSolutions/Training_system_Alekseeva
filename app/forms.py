from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, validators
from wtforms.validators import InputRequired, EqualTo, ValidationError
from app.models import Users


class LoginForm(FlaskForm):
    login = StringField("Логин", validators=[InputRequired()])
    password = PasswordField("Пароль", validators=[InputRequired()])
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    user_name = StringField("Имя", validators=[InputRequired()])
    user_login = StringField("Логин", validators=[InputRequired()])
    user_password = PasswordField("Пароль", validators=[InputRequired()])
    user_cpassword = PasswordField("Пароль", validators=[InputRequired(), EqualTo("user_password", message="Passwords must match !")])
    submit = SubmitField("Зарегистрироваться")

    def validate_uname(self, user_name):
        if Users.query.filter_by(username=user_name.data).first():
            raise ValidationError("Username already taken!")
        
class SettingsForm(FlaskForm):
    user_name = StringField(label="Ваше имя", validators=[validators.Length(max=32)])
    old_password = PasswordField('Старый пароль', validators=[validators.Optional()])
    new_password = PasswordField('Новый пароль', validators=[validators.Optional()])
    confirm_password = PasswordField('Повторите новый пароль', validators=[validators.EqualTo('new_password', message='Пароли должны совпадать')])
    scoring_system = SelectField('Система оценивания', coerce=int, validators=[validators.InputRequired()])
    submit = SubmitField("Сохранить изменения")