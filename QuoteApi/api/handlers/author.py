from api import db, app
from flask import request, abort, jsonify
from http import HTTPStatus
from api.models.author import AuthorModel
from api.models.quote import QuoteModel
from marshmallow import ValidationError, EXCLUDE
from sqlalchemy.exc import SQLAlchemyError
from api.schemas.author import author_schema, authors_schema, change_author_schema


@app.get("/authors")
def get_authors():
    """GET List of Authors + """
    authors_db = db.session.scalars(db.select(AuthorModel)).all()
    # authors = [author.to_dict() for author in authors_db]
    # return jsonify(authors), 200
    return jsonify(authors_schema.dump(authors_db)), HTTPStatus.OK


@app.get("/authors/<int:author_id>")
def author_quotes(author_id: int):
    """GET Author by ID + """
    author_db = db.get_or_404(AuthorModel, author_id, description=f'Author with id={author_id} not found')
    # return jsonify(author.to_dict()), HTTPStatus.OK
    return jsonify(author_schema.dump(author_db)), HTTPStatus.OK

@app.post("/authors")
def create_author():
    """Create new Author + """
    # data = request.json
    try:
        author_data = author_schema.loads(request.data)  # get_data() return raw bytes
        author = AuthorModel(**author_data)
        db.session.add(author)
        db.session.commit()
    except ValidationError as ve:
        abort(HTTPStatus.BAD_REQUEST, f'Validation error: {str(ve)}')
    # except TypeError:
    #     abort(400, f"Invalid data. Required: <name>, <surname>. Received: {', '.join(data.keys())}.")
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(HTTPStatus.SERVICE_UNAVAILABLE, f"Database error: {str(e)}")
    # return jsonify(author.to_dict()), 201
    return jsonify(author_schema.dump(author)), HTTPStatus.CREATED


@app.delete("/authors/<int:author_id>")
def delete_author(author_id):
    """Delete Author by ID + """
    author = db.get_or_404(entity=AuthorModel, ident=author_id, description=f"Author with id={author_id} not found")
    db.session.delete(author)
    try:
        db.session.commit()
        return jsonify({"message": f"Author with id {author_id} has deleted."}), HTTPStatus.OK
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(HTTPStatus.SERVICE_UNAVAILABLE, f"Database error: {str(e)}")


@app.put("/authors/<int:author_id>")
def edit_author(author_id: int):
    """Edit Author by ID + """
    # new_data = request.json

    try:
        new_data = change_author_schema.load(request.json, unknown=EXCLUDE)
    except ValidationError as ve:
        abort(HTTPStatus.BAD_REQUEST, f'Validation error: {str(ve)}')

    if not new_data:
        return abort(HTTPStatus.BAD_REQUEST, "No valid data to update")
    
    author = db.get_or_404(entity=AuthorModel, ident=author_id, description=f"Author with id={author_id} not found")

    try:
        for key_as_attr, value in new_data.items():
            # if not hasattr(author, key_as_attr):
            #     raise Exception(f"Invalid key='{key_as_attr}'. Valid only {tuple(vars(author).keys())}")
            setattr(author, key_as_attr, value)

        db.session.commit()
        return jsonify(author_schema.dump(author)), HTTPStatus.OK
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(HTTPStatus.SERVICE_UNAVAILABLE, f"Database error: {str(e)}")
