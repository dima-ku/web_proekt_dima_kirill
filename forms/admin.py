from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.fields.core import IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired

class BookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    link = StringField('Ссылка на Яндекс.Диск', default='')
    info = TextAreaField('Краткое описание книги')
    img = StringField('Картинка', validators=[DataRequired()])
    year = IntegerField('Год написания', validators=[DataRequired()])
    submit = SubmitField('Сохранить')