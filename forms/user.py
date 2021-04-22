from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    about = TextAreaField('О себе')
    submit = SubmitField('Войти')

class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class UserEditForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    name = StringField('Отображаемое Имя', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired()])
    changed_password = PasswordField('Пароль')
    about = TextAreaField('О себе')
    favourite_books = BooleanField('Показывать понравившиеся книги другим пользователям')
    submit = SubmitField('Сохранить')

