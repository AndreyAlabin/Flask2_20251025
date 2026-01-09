from api import ma
from api.models.user import UserModel
from flask import request
from marshmallow import validate, fields, post_load


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        exclude= ("password_hash",)
        dump_only = ("id",)


    username = ma.auto_field(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=8))

    @post_load
    def make_user(self, data, **kwargs):
        if request.method == "POST":
            return UserModel(**data)
        return data

user_schema = UserSchema()
