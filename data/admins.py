from data.favourite_books import FavouriteBook
from data.comments import Comment
from data.ratings import Rating
from forms.admin import BookForm
from flask import session, redirect, url_for
from flask_login import current_user
from .db_session import create_session
from .users import User
from flask import request
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin import BaseView, expose
from flask_admin import AdminIndexView
import json
from .books import Book
import uuid
import meilisearch



class MyModelView(ModelView):
    form_excluded_columns = ['hashed_password']
    column_exclude_list = ['hashed_password']

    def is_accessible(self):
        db_sess = create_session()
        return current_user.is_authenticated and db_sess.query(User).filter(User.id == session['user_id']).first().admin
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'))

class MyFileAdmin(FileAdmin):
    def is_accessible(self):
        db_sess = create_session()
        return current_user.is_authenticated and db_sess.query(User).filter(User.id == session['user_id']).first().admin
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'))

class BookView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        if request.method == 'POST':
            id = request.form['input']
            if request.form['option'] == 'edit':
                db_sess = create_session()
                if db_sess.query(Book).filter(Book.id == id).first():
                    return redirect(f'/admin/bookview/edit/{id}')
            if request.form['option'] == 'delete':
                db_sess = create_session()
                if db_sess.query(Book).filter(Book.id == id).first():
                    return redirect(f'/admin/bookview/delete/{id}')
                
        return self.render('admin/bookview_index.html')
    
    @expose('/add', methods=['GET', 'POST'])
    def add(self):
        form = BookForm()
        if request.method == 'POST':
            id = uuid.uuid4()
            d = {}
            d['id'] = str(id)
            d['title'] = form.title.data
            d['author'] = form.author.data
            d['link'] = form.link.data
            d['info'] = form.info.data
            d['img'] = form.img.data
            d['year'] = form.year.data
            with open('./db/books.json') as f:
                data = json.load(f)
            data.append(d)
            with open('./db/books.json', 'w') as f:
                json.dump(data, f)
            db_sess = create_session()
            book = Book()
            book.id = str(id)
            book.title = form.title.data
            db_sess.add(book)
            db_sess.commit()
            client = meilisearch.Client('http://127.0.0.1:8080')

            json_file = open('db/books.json')
            books = json.load(json_file)
            client.index('books').delete()
            client.index('books').add_documents(books)
            return redirect('/admin/')
        return self.render('admin/book_interface.html', form=form)
    
    @expose('/edit/<book_id>', methods=['GET', 'POST'])
    def edit(self, book_id):
        form = BookForm()
        if request.method == 'POST':
            with open('./db/books.json') as f:
                data = json.load(f)
                for i in range(len(data)):
                    if data[i]['id'] == book_id:
                        data[i]['title'] = form.title.data
                        data[i]['author'] = form.author.data
                        data[i]['link'] = form.link.data
                        data[i]['info'] = form.info.data
                        data[i]['img'] = form.img.data
                        data[i]['year'] = form.year.data
            with open('./db/books.json', 'w') as f:
                json.dump(data, f)
            db_sess = create_session()
            book = db_sess.query(Book).filter(Book.id == book_id).first()
            book.title = form.title.data
            db_sess.commit()
            
            client = meilisearch.Client('http://127.0.0.1:8080')

            json_file = open('db/books.json')
            books = json.load(json_file)
            client.index('books').delete()
            client.index('books').add_documents(books)

            return redirect('/admin/')
        book = {}
        with open('./db/books.json') as f:
            data = json.load(f)
            for i in data:
                if i['id'] == book_id:
                    book = i
        form.title.data = book['title']
        form.author.data = book['author']
        form.link.data = book['link']
        form.info.data = book['info']
        form.img.data = book['img']
        form.year.data = book['year']
        return self.render('/admin/book_interface.html', form=form)
    
    @expose('/delete/<book_id>')
    def delete(self, book_id):
        db_sess = create_session()
        db_sess.query(Rating).filter(Rating.book_id == book_id).delete()
        db_sess.query(Comment).filter(Comment.book_id == book_id).delete()
        db_sess.query(FavouriteBook).filter(FavouriteBook.book_id == book_id).delete()
        db_sess.query(Book).filter(Book.id == book_id).delete()
        db_sess.commit()
        data = []
        with open('./db/books.json') as f:
            data = json.load(f)
        d = 0
        for i in range(len(data)):
            if data[i]['id'] == book_id:
                d = i
                break
        data.pop(i)
        with open('./db/books.json', 'w') as f:
            json.dump(data, f)
                
        client = meilisearch.Client('http://127.0.0.1:8080')

        json_file = open('db/books.json')
        books = json.load(json_file)
        client.index('books').delete()
        client.index('books').add_documents(books)
        return redirect('/admin/bookview')

    def is_accessible(self):
        db_sess = create_session()
        return current_user.is_authenticated and db_sess.query(User).filter(User.id == session['user_id']).first().admin
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'))

class MyIndexView(AdminIndexView):
    def is_accessible(self):
        db_sess = create_session()
        return current_user.is_authenticated and db_sess.query(User).filter(User.id == session['user_id']).first().admin
    
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login'))