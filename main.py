from flask import Flask
from data import db_session
from data.users import User
from flask import render_template
from flask_wtf import FlaskForm
from templates import *
from flask_login import LoginManager, login_user, login_required
from forms.user import RegisterForm
from forms.user import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
@app.route('/index')
@app.route('/register', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
@login_manager.user_loader
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# -_-
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def index():
    user = "dima"
    return render_template('index.html', title='Домашняя страница',
                           username=user)


def main():
    db_session.global_init("db/users_db.db")
    app.run()


if __name__ == '__main__':
    main()
