import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Rating(SqlAlchemyBase):
    __tablename__ = 'ratings'

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    book_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('books.id'))
    rating = sqlalchemy.Column(sqlalchemy.Float)
    user = orm.relation('User')
    book = orm.relation('Book')
