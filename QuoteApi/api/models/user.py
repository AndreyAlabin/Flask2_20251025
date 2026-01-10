from http import HTTPStatus
from flask import abort
from passlib.apps import custom_app_context as pwd_context
import sqlalchemy.orm as so
import sqlalchemy as sa
from api import db
from config import Config
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
# from itsdangerous import URLSafeSerializer, BadSignature
import jwt
from time import time


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

    def generate_auth_token(self):
        # s = URLSafeSerializer(Config.SECRET_KEY)
        # return s.dumps({'id': self.id})
        token = jwt.encode({"id": self.id, "exp": int(time()) + 600}, Config.SECRET_KEY, algorithm="HS256")
        return token


    @staticmethod
    def verify_auth_token(token):
        # s = URLSafeSerializer(Config.SECRET_KEY)
        # print(f'{token = }')
        try:
            # data = s.loads(token)
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        # except BadSignature as bde:
        except Exception as e:
            # print(f'{bde = }')
            # print(f'{str(e) = }')
            return None  # invalid token
        user = db.get_or_404(UserModel, data['id'], description=f'User with id {data["id"]} does not found')
        return user
