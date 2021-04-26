from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):  # форма добавления/изменения отзыва
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    picture = FileField('Добавьте изображения')
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')