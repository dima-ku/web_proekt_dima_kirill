from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired

class CommentForm(FlaskForm):
    content = TextAreaField('Ваш Отзыв', validators=[DataRequired()])
    anonymous = BooleanField('Анонимно')
    submit = SubmitField('Оставить отзыв')
