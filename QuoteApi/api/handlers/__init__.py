from api import app
from flask import jsonify
from werkzeug.exceptions import HTTPException


# def check(data: dict, check_rating=False) -> tuple[bool, dict]:
#     keys = ('text', )
#     if check_rating:
#         rating = data.get('rating')
#         if rating and rating not in range(1, 6):
#             return False, {"error": "Rating must be between 1 and 5"}
#         else:
#             keys += ('rating', )
#     if set(data.keys()) - set(keys):
#         return False, {"error": "Invalid fields to create/update"}
#     return True, data


@app.errorhandler(HTTPException)
def handle_exception(e):
    """ Функция для перехвата HTTP ошибок и возврата в виде JSON."""
    return jsonify({"error": str(e)}), e.code
