import meilisearch
import json
import os
from flask import Flask, request, redirect
from flask.globals import session
from flask.helpers import send_from_directory, url_for
from flask.templating import render_template
from flask import Flask, render_template, redirect, abort
from flask_login import LoginManager, login_user, login_required, logout_user
from data.db_session import global_init, create_session
from data.users import User
from data.ratings import Rating
from data.books import Book
from data.favourite_books import FavouriteBook
from forms.user import RegisterForm, LoginForm, UserEditForm
from forms.comment import CommentForm
from data.comments import Comment
from flask_admin import Admin
from data.admins import MyModelView, BookView, MyFileAdmin, MyIndexView
from flask_restful import Api
from api.books_resources import BookResource, BookIdResource, BookListResource
from password_strength import PasswordPolicy

policy = PasswordPolicy.from_names(
    length=8,
    uppercase=2,
    numbers=2
)


client = meilisearch.Client('http://127.0.0.1:8080')

json_file = open('db/books.json')
books = json.load(json_file)
client.index('books').delete()
client.index('books').add_documents(books)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['FLASK_ADMIN_SWATCH'] = 'paper'

global_init('db/db.db')

login_manager = LoginManager(app)

admin = Admin(app, template_mode='bootstrap3', index_view=MyIndexView())
admin.add_view(MyModelView(User, create_session()))
admin.add_view(MyModelView(Book, create_session()))
admin.add_view(MyModelView(Comment, create_session()))
admin.add_view(MyModelView(Rating, create_session()))
admin.add_view(MyFileAdmin('static/files', name='Files'))
admin.add_view(BookView())

api = Api(app)
api.add_resource(BookResource, '/api/books/request/<request>')
api.add_resource(BookListResource, '/api/books/all')
api.add_resource(BookIdResource, '/api/books/id/<book_id>')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        search_request = request.form['search_bar']
        return redirect(f'/search/{search_request}/1')
    return redirect('/best/1')


@app.route('/best/<int:page>')
def best(page):
    if page < 1:
        abort(404)
    param = {}
    param['title'] = 'Лучший сайт по поиску книг'
    books = []
    db_sess = create_session()
    books = db_sess.query(Rating).filter(Rating.rating >= 4).all()
    book_ids = []
    for book in books:
        book_ids.append(book.book_id)
    books = []
    with open('db/books.json') as f:
        data = json.load(f)
        for book in data:
            if book['id'] in book_ids:
                books.append(book)
    pages = {}
    pages['page'] = page
    pages["next_page"] = None
    if 10 * (page + 1) <= len(books) + 10:
        pages["next_page"] = page + 1
    pages["previous_page"] = None
    if page > 1:
        pages["previous_page"] = page - 1
    return render_template('best.html', param=param, books=books[10 * (page - 1): min(10 * page, len(books))], pages=pages)


@app.route('/search/<search_request>/<int:page>')
def search_result(search_request, page):
    param = {}
    param['title'] = search_request
    books = client.index('books').search(search_request)['hits']

    pages = {}
    pages['page'] = page
    pages["next_page"] = None
    if 10 * (page + 1) <= len(books) + 10:
        pages["next_page"] = page + 1
    pages["previous_page"] = None
    if page > 1:
        pages["previous_page"] = page - 1
    return render_template('search_result.html', param=param, books=books[10 * (page - 1): min(10 * page, len(books))], pages=pages)


@app.route('/books/<book_id>', methods=['GET', 'POST'])
def book_page(book_id):
    db_sess = create_session()
    if request.method == 'POST':
        rating = db_sess.query(Rating).filter(
            Rating.user_id == session['user_id'], Rating.book_id == book_id).first()
        res = request.form.to_dict()
        if rating:
            db_sess.delete(rating)
            if 'star1' in res:
                rating.rating = 5
            elif 'star2' in res:
                rating.rating = 4
            elif 'star3' in res:
                rating.rating = 3
            elif 'star4' in res:
                rating.rating = 2
            elif 'star5' in res:
                rating.rating = 1
            db_sess.add(rating)
        else:
            rating = Rating()
            rating.user = db_sess.query(User).filter(
                User.id == session['user_id']).first()
            rating.book_id = book_id
            if 'star1' in res:
                rating.rating = 5
            elif 'star2' in res:
                rating.rating = 4
            elif 'star3' in res:
                rating.rating = 3
            elif 'star4' in res:
                rating.rating = 2
            elif 'star5' in res:
                rating.rating = 1
            db_sess.add(rating)
        db_sess.commit()
    param = {}
    with open('db/books.json') as f:
        data = json.load(f)
        for book in data:
            if book['id'] == book_id:
                param['book'] = book
                break
    param['title'] = param['book']['title']
    rating = 0
    if 'user_id' in session and session['user_id']:
        rating = db_sess.query(Rating).filter(
            Rating.user_id == session['user_id'], Rating.book_id == book_id).first()
    if rating:
        param['user_rating'] = rating.rating
    ratings = db_sess.query(Rating).filter(Rating.book_id == book_id).all()
    book_rating = 0
    c = 0
    for r in ratings:
        book_rating += r.rating
        c += 1
    c = max(c, 1)
    param['rating'] = round(book_rating / c, 1)
    if 'user_id' in session:
        param['favourite'] = db_sess.query(FavouriteBook).filter(
            FavouriteBook.user_id == session['user_id'], FavouriteBook.book_id == book_id).first()
    comments = db_sess.query(Comment).filter(Comment.book_id == book_id).all()
    return render_template('book.html', param=param, comments=reversed(comments), exists=os.path.isfile(f'static/files/{book_id}.pdf'))


@app.route('/books/<book_id>/download')
def download(book_id):
    return send_from_directory(app.config['UPLOAD_FOLDER'], f'{book_id}.pdf', as_attachment=True)


@app.route('/books/<book_id>/<r>/favourite')
@login_required
def favourite(book_id, r):
    db_sess = create_session()
    fav = db_sess.query(FavouriteBook).filter(
        FavouriteBook.user_id == session['user_id'], FavouriteBook.book_id == book_id).first()
    if fav:
        db_sess.delete(fav)
    else:
        fav = FavouriteBook()
        fav.book_id = book_id
        fav.user_id = session['user_id']
        db_sess.add(fav)
    db_sess.commit()
    if r == 'users':
        return redirect(f"/users/{session['user_id']}")
    else:
        return redirect(f'/books/{book_id}')


@app.route('/books/<book_id>/add_comment', methods=['GET', 'POST'])
@login_required
def add_comment(book_id):
    form = CommentForm()
    if form.validate_on_submit():
        db_sess = create_session()
        comment = Comment(
            book_id=book_id,
            user_id=session['user_id'],
            anonymous=form.anonymous.data,
            content=form.content.data)
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f'/books/{book_id}')
    return render_template('comment.html', title='Отзыв', form=form)


@app.route('/books/<comment_id>/edit_comment', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    form = CommentForm()
    if request.method == 'GET':
        db_sess = create_session()
        comment = db_sess.query(Comment).filter(
            Comment.id == comment_id).first()
        if comment.user_id == session['user_id']:
            form.content.data = comment.content
            form.anonymous.data = comment.anonymous
        else:
            return "Not Found"
    if request.method == 'POST':
        db_sess = create_session()
        comment = db_sess.query(Comment).filter(
            Comment.id == comment_id).first()
        if comment.user_id == session['user_id']:
            comment.content = form.content.data
            comment.anonymous = form.anonymous.data
            db_sess.commit()
            return redirect(f'/books/{comment.book_id}')
        else:
            return "Not Found"
    return render_template('comment.html', form=form)


@app.route('/books/<comment_id>/delete_comment')
@login_required
def delete_comment(comment_id):
    db_sess = create_session()
    comment = db_sess.query(Comment).filter(Comment.id == comment_id).first()
    book_id = comment.book_id
    db_sess.delete(comment)
    db_sess.commit()
    return redirect(f'/books/{book_id}')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        
        if (form.password.data != '' and policy.test(form.password.data) != []) or form.password.data.upper() == form.password.data:
            error = 'Слабый пароль. Длина > 8. Необходимо хотя бы 2 заглавные буквы(но не все) и 2 цифры'
            return render_template('register.html', title='Регистрация', form=form, errors=error)
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


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = create_session()
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            session['user_id'] = user.id
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/users/<user_id>')
def user_page(user_id):
    db_sess = create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    books = []
    if db_sess.query(FavouriteBook).filter(FavouriteBook.user_id == user_id):
        favs = db_sess.query(FavouriteBook).filter(
            FavouriteBook.user_id == user_id)
        book_ids = []
        for fav in favs:
            book_ids.append(fav.book_id)
        with open('db/books.json') as f:
            data = json.load(f)
            for book in data:
                if book['id'] in book_ids:
                    books.append(book)

    return render_template('user_page.html', user=user, books=books)


@app.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    form = UserEditForm()
    error = ''
    if request.method == 'GET':
        db_sess = create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        if user.id == session['user_id']:
            form.name.data = user.name
            form.email.data = user.email
            form.about.data = user.about
            form.favourite_books.data = user.show_favourite_books
        else:
            return "Not Found"
    if request.method == 'POST':
        db_sess = create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        if user.id == session['user_id']:
            if (form.changed_password.data != '' and policy.test(form.changed_password.data) != []) or form.changed_password.data.upper() == form.changed_password.data:
                error = 'Слабый пароль. Длина > 8. Необходимо хотя бы 2 заглавные буквы(но не все) и 2 цифры'
            elif user.check_password(form.current_password.data):
                user.name = form.name.data
                user.email = form.email.data
                if form.changed_password.data != '':
                    user.set_password(form.changed_password.data)
                user.about = form.about.data
                user.show_favourite_books = form.favourite_books.data
                db_sess.commit()
                return redirect('/')
            else:
                error = 'Неправильный пароль'
        else:
            return "Not Found"

    return render_template('edit_user.html', form=form, errors=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session['user_id'] = ''
    return redirect("/")


app.run(debug=True)