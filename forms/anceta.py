from flask_wtf import FlaskForm, Form
from wtforms import BooleanField, SubmitField, PasswordField, FormField, StringField, DateTimeField, TextAreaField
from wtforms.fields.html5 import EmailField, IntegerField
from wtforms.validators import DataRequired, Email


class QuestionaryForm(FlaskForm):  # форма анкета
    email = EmailField('Почта', validators=[DataRequired()])
    name_ful = StringField('Ваше ФИО', validators=[DataRequired()])
    place = StringField('Место проведения праздника', validators=[DataRequired()])
    data_holiday = StringField('Дата и время проведения торжества', validators=[DataRequired()])
    mobile_phone = StringField("Ваш мобильный телефон", validators=[DataRequired()])
    holiday = StringField('Какое мероприятие', validators=[DataRequired()])
    number_of_guests = StringField('Количество гостей', validators=[DataRequired()])
    submit = SubmitField('Отправить заявку на проведение торжества')