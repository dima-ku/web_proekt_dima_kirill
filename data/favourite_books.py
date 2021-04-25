from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm

class FavouriteBook(SqlAlchemyBase):
    __tablename__ = 'favourite_books'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False)
    book_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('books.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    book = orm.relation('Book')
    user = orm.relation('User')