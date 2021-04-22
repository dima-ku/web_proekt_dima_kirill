import datetime
import sqlalchemy
from sqlalchemy.sql.schema import ForeignKey
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    book_id = sqlalchemy.Column(sqlalchemy.Integer)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    anonymous = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    content = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.Date, default=datetime.datetime.date(datetime.datetime.now()))
    user = orm.relation('User')