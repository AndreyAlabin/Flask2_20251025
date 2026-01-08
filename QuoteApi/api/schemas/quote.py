from functools import partial

from api import ma
from api.models.quote import QuoteModel
from api.schemas.author import AuthorSchema
from marshmallow import EXCLUDE
from marshmallow.validate import Range, Length


# def rating_validate(value: int):
#     return value in range(1, 6)


class QuoteSchema(ma.SQLAlchemySchema):
    class Meta:
        model = QuoteModel
        unknown = EXCLUDE
        dump_only = ('id',)
        # load_instance = True

    id = ma.auto_field()
    text = ma.auto_field(required=True, validate=Length(min=1))
    # author_id = ma.auto_field()
    author = ma.Nested(AuthorSchema(only=('id', 'name', 'surname',)))
    rating = ma.auto_field(strict=True, validate=Range(1, 5))

quote_schema = QuoteSchema()  # exclude=['author_id']
quotes_schema = QuoteSchema(many=True)
# change_quotes_schema = QuoteSchema(load_instance=False)
change_quotes_schema = QuoteSchema(only=('rating', 'text',), partial=True)
change_quotes_without_rating = QuoteSchema(only=('text',), partial=True)
quotes_schema_without_author = QuoteSchema(many=True, exclude=['author'])
