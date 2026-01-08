from functools import partial

from api import ma
from api.models.author import AuthorModel
from marshmallow.validate import Length


class AuthorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AuthorModel
        dump_only = ('id',)
        # load_instance = True

    name = ma.auto_field(required=True, validate=Length(1, 32))
    surname = ma.auto_field(required=True, validate=Length(1, 32))


author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)
change_author_schema = AuthorSchema(load_instance=False, partial=True)
