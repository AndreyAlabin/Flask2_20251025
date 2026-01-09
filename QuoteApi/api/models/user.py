from http import HTTPStatus
from flask import abort
from passlib.apps import custom_app_context as pwd_context
import sqlalchemy.orm as so
from api import db
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class UserModel(db.Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(32), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(128))

    def __init__(self, username, password):
        self.username = username
        self.hash_password(password)

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as e:
            abort(HTTPStatus.BAD_REQUEST, f'{str(e.orig)}')
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(HTTPStatus.SERVICE_UNAVAILABLE, f'{str(e)}')

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(HTTPStatus.SERVICE_UNAVAILABLE, f'{str(e)}')
