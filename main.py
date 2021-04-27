import csv
import datetime
import os

from flask import Flask, render_template, request, make_response, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.exceptions import abort
from flask_restful import reqparse, abort, Api
from werkzeug.utils import redirect
from data import db_session, news_api, news_resources
from data.news import News
from data.orders import Order
from data.users import User
from forms.anceta import QuestionaryForm
from forms.login import LoginForm
from forms.news import NewsForm
from forms.user import RegisterForm

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/contacts')  # страница контактов
def contacts():
    return render_template('contacts.html')  # подключаем шаблон страницы


@app.route('/galery')  # страница фотогалереи
def galery():
    return render_template('galery.html')


@app.route('/')  # главная страница
def portfolio():
    return render_template('portfolio.html')


@app.route('/anceta_csv_convert')  # страница для скачивания файла csv с заказами
def convert_csv():
    return render_template('csv.html')


@app.route('/price')  # страница с тарифами
def price():
    return render_template('pricing.html')


@app.route('/successful_order')  # страница появляется, когда пользователь успешно сделал заявку на проведение мероприятия
def successful_order():
    return render_template('successful_order.html')


@app.route('/anceta', methods=['GET', 'POST'])  # страница с анкетой для заказа
def anceta():
    form = QuestionaryForm()  # подключение к форме с вопросами
    if form.validate_on_submit():
        db_sess = db_session.create_session()  # создаем сессию бд
        order = Order(
            name=form.name_ful.data,
            email=form.email.data,
            place=form.place.data,
            data_holiday=form.data_holiday.data,
            mobile_phone=form.mobile_phone.data,
            holiday=form.holiday.data,
            number_of_guests=form.number_of_guests.data)  # добавление заказа в бд
        db_sess.add(order)
        db_sess.commit()
        orders = db_sess.query(Order).all()
        with open('static/orders.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"')
            for order in orders:
                print(order)
                writer.writerow([order.name, order.place, order.email, order.data_holiday, order.mobile_phone,
                                 order.holiday,
                                 order.number_of_guests, order.created_date])
        return redirect('/successful_order')  # перенаправляем на страницу успешного заказа
    return render_template('anceta.html', form=form)


@app.route("/reviews")  # страница с отзывами
def index():
    db_sess = db_session.create_session()  # сессия бд
    if current_user.is_authenticated:  # если пользователь авторизован
       news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))  # если отзывы пользователя или они не приватные
    else:
        news = db_sess.query(News).filter(News.is_private != True)  # если пользователь не авторизован, выводим все не приватные отзывы
    return render_template("index.html", news=news)


@app.route('/register', methods=['GET', 'POST'])  # страница регистрации
def reqister():
    form = RegisterForm()  # загружаем форму регистрации
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:  # если пароли не совпадают, выводим соответствующее сообщение
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()  # создаем сессию бд
        if db_sess.query(User).filter(User.email == form.email.data).first():  # если такой пользователь уже есть
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )   # если все поля заполнены правильно, хэшируем пароль и добавляем пользователя в бд
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')  # переходим на страницу авторизации
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])  # страница авторизации
def login():
    form = LoginForm()  # форма авторизации
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()  # пользователь с таким email из бд
        if user and user.check_password(form.password.data):  # если такой пользователь есть и введён правильный пароль
            login_user(user, remember=form.remember_me.data)  # авторизуем пользователя
            return redirect("/")  # перенаправляем на главную страницу
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)  # если пользователя не существует или введён неправильный пароль
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')  # выход из профиля
def logout():
    logout_user()
    return redirect("/")  # перенаправляем на главную


@app.route('/news',  methods=['GET', 'POST'])  # страница добавления отзыва
@login_required   # доступно только авторизованным пользователям
def add_news():
    form = NewsForm()  # форма добавления отзыва
    if form.validate_on_submit():
        db_sess = db_session.create_session()  # сессия бд
        news = News()  # создаем новый отзыв в бд
        news.title = form.title.data  # добавляем данные в поля
        news.content = form.content.data
        news.is_private = form.is_private.data
        news.picture = form.picture.data
        current_user.news.append(news)  # добавляем отзыв у пользователя
        db_sess.merge(current_user)  # связываем отзыв с текущим пользователем
        db_sess.commit()  # сохраняем изменения
        return redirect('/reviews')  # переходим на страницу отзывов
    return render_template('news.html', title='Добавление отзыва',
                           form=form)


@app.route('/news<int:id>', methods=['GET', 'POST'])  # страница редактирования отзыва
@login_required  # доступно только авторизованным пользователям
def edit_news(id):
    form = NewsForm()  # форма отзыва
    if request.method == "GET":  # метод получения данных
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()  # берем данные нужного отзыва из бд
        if news:  # если такой отзыв есть, добавляем в поля формы данные из бд
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:  # если отзыва нет, вызываем ошибку 404
            abort(404)
    if form.validate_on_submit():  # если кнопка применить нажата
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:  # обновляем бд
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/reviews')  # преходим на страницу отзывов
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование отзыва',
                           form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])  # страница для удаления отзыва
@login_required  # доступно только авторизованным пользователям
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()  # ищем нужный отзыв в бд
    if news:  # если отзыв есть, удаляем
        db_sess.delete(news)
        db_sess.commit()
    else:  # если отзыва нет, вызываем ошибку 404
        abort(404)
    return redirect('/reviews')  # переходим на страницу отзывов


@app.errorhandler(404)  # выполняется при ошибке 404
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)  # возвращаем сообщение об ошибке 404 в формате json


def main():  # вызывается при запуске программы
    db_session.global_init("db/blogs.db")  # создаём бд
    # для списка объектов
    api.add_resource(news_resources.NewsListResource, '/api/v2/news')
    # для одного объекта
    api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
