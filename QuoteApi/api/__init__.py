from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_httpauth import HTTPBasicAuth


class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.json.ensure_ascii = False
app.config.from_object('config.DevConfig')

db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)
ma = Marshmallow()
ma.init_app(app)
auth = HTTPBasicAuth(app)

@auth.verify_password
def verify_password(username, password):
    from api.models.user import UserModel
    user = db.one_or_404(db.select(UserModel).filter_by(username=username))
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


from api.handlers import author
from api.handlers import quote
from api.handlers import user
