from http import HTTPStatus
from api import db, app
from flask import jsonify, abort, request
from api.models.quote import QuoteModel
from api.models.author import AuthorModel
from marshmallow import ValidationError, EXCLUDE
# from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError  # InvalidRequestError
# from . import check
from api.schemas.quote import quote_schema, quotes_schema, quotes_schema_without_author, change_quotes_schema, change_quotes_without_rating


@app.get("/quotes")
def get_quotes():
    """GET List of Quotes + """
    quotes_db = db.session.scalars(db.select(QuoteModel)).all()
    # quotes = []
    # for quote in quotes_db:
    #     quotes.append(quote.to_dict())
    return jsonify(quotes_schema.dump(quotes_db)), HTTPStatus.OK


@app.get("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id: int):
    """GET Quote by ID + """
    quote_db = db.get_or_404(QuoteModel, quote_id, description=f"Quote with id={quote_id} not found")
    return jsonify(quote_schema.dump(quote_db)), HTTPStatus.OK


@app.delete("/quotes/<int:quote_id>")
def delete_quote(quote_id):
    """Delete Quote by ID + """
    quote = db.get_or_404(entity=QuoteModel, ident=quote_id, description=f"Quote with id={quote_id} not found")
    db.session.delete(quote)
    try:
        db.session.commit()
        return jsonify({"message": f"Quote with id {quote_id} has deleted."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(503, f"Database error: {str(e)}")


@app.post("/authors/<int:author_id>/quotes")
def create_quote(author_id: int):
    """Create new Quote by Author ID + """
    author = db.get_or_404(AuthorModel, author_id, description=f"Author with id={author_id} not found")
    # data = request.json

    try:
        quote_db = quote_schema.loads(request.data)
        quote = QuoteModel(author, **quote_db)
        db.session.add(quote)
        db.session.commit()
    except ValidationError as ve:
        abort(HTTPStatus.BAD_REQUEST, f'Validation Error: {str(ve)}')
    # except TypeError:
    #     abort(HTTPStatus.BAD_REQUEST, f"Invalid data. Required: <author>, <text>, <rating>. Received: {', '.join(data.keys())}.")
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(HTTPStatus.SERVICE_UNAVAILABLE, f"Database error: {str(e)}")
    return jsonify(quote_schema.dump(quote)), HTTPStatus.CREATED


@app.get("/authors/<int:author_id>/quotes")
def get_quote_by_author_id(author_id: int):
    """GET List of Quotes by Author ID + """
    author = db.get_or_404(AuthorModel, author_id, description=f"Author with id={author_id} not found")
    # quotes_db = db.session.scalars(db.select(QuoteModel).where(QuoteModel.author_id == author_id)).all()
    # quotes_list = [q.to_dict() for q in quotes_db]
    # return jsonify(quotes_list), HTTPStatus.OK
    return jsonify({"author": [author.name, author.surname]} | {"quotes": quotes_schema_without_author.dump(list(author.quotes))}), HTTPStatus.OK


@app.put("/quotes/<int:quote_id>")
def edit_quote(quote_id: int):
    """Edit Quote by ID + """

    try:
        new_data = change_quotes_schema.load(request.json, unknown=EXCLUDE)
    except ValidationError as ve:
        if ve.messages_dict['rating']:
            new_data = change_quotes_without_rating.load(request.json, unknown=EXCLUDE)
        else:
            abort(HTTPStatus.BAD_REQUEST, f'Validation error: {str(ve.messages_dict)}')

    if not new_data:
        return abort(HTTPStatus.BAD_REQUEST, "No valid data to update")

    quote = db.get_or_404(entity=QuoteModel, ident=quote_id, description=f"Quote with id={quote_id} not found")

    try:
        for key_as_attr, value in new_data.items():
            setattr(quote, key_as_attr, value)

        db.session.commit()
        return jsonify(quote_schema.dump(quote)), HTTPStatus.OK
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(HTTPStatus.SERVICE_UNAVAILABLE, f"Database error: {str(e)}")


""""
@app.route("/quotes/filter", methods=["GET"])
def filter_quotes():
    data = request.args
    try:
        quotes = db.session.scalars(db.select(QuoteModel).filter_by(**data)).all()
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, f'Error: {str(e)}')

    return jsonify((quotes_schema.dump(quotes))), HTTPStatus.OK


Этот код не рабочий, когда нужны подзапросы в модель автора по name или surname через модель цитат

Пример запроса: /quotes/filter?rating=4&author=Belov
Выдаёт ошибку: "400 Bad Request: Error: Mapped instance expected for relationship comparison to object. 
Classes, queries and other SQL elements are not accepted in this context; 
for comparison with a subquery, use QuoteModel.author.has(**criteria).""

Пример запроса: /quotes/filter?rating=4&surname=Belov
Выдаёт ошибку: "400 Bad Request: Error: Entity namespace for "quotes" has no property "surname""

Не спасла также попытка сделать select через множественные условия в filter_by,
так как в случаях, когда на выходе под условие попадает несколько авторов,
и в filter_by нужно задать условие (QuoteModel.author_id in authors_id), то выдаёт другую ошибку: 
TypeError: Select.filter_by() takes 1 positional argument but 2 were given
"""

# В итоге задачу запроса из базы пока решил по-другому, он отрабатывает любой набор параметров,
# а со сложными подзапросами SQLAlchemy-ma буду ещё разбираться.
# Вывод результата сделал с использованием ma
@app.get("/quotes/filter")
def filter_quote():
    data = request.args
    if not list(set(data.keys()).intersection({'name', 'surname', 'text', 'rating'})):
        abort(HTTPStatus.BAD_REQUEST,
              f"Request is empty. Required: name, surname, text, rating. Received: {', '.join(data.keys())}.")

    data_author = dict()
    data_quote = dict()
    for n in ['name', 'surname', 'text', 'rating']:
        if data.get(n):
            match n :
                case 'name' | 'surname' : data_author[n] = data.get(n)
                case 'text' | 'rating' : data_quote[n] = data.get(n)

    quotes_db = []
    if data_author:
        authors_id = db.session.scalars(db.select(AuthorModel.id).filter_by(**data_author)).all()
        if authors_id:
            for a in authors_id:
                data_quote['author_id'] = a
                quotes_db.extend(db.session.scalars(db.select(QuoteModel).filter_by(**data_quote)).all())
    else:
        quotes_db.extend(db.session.scalars(db.select(QuoteModel).filter_by(**data_quote)).all())

    return jsonify(quotes_schema.dump(quotes_db)), HTTPStatus.OK