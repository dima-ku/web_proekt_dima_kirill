import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Book(SqlAlchemyBase):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String)
    date_added = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    ratings = orm.relation('Rating', back_populates='book')
