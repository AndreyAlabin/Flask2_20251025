from api import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from api.models.quote import QuoteModel


class AuthorModel(db.Model):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True)
    surname: Mapped[str] = mapped_column(String(32), server_default="-", index=True, unique=False)
    quotes: Mapped[list['QuoteModel']] = relationship(lambda:QuoteModel, back_populates='author', lazy='dynamic', cascade="all, delete-orphan") # type: ignore

    def __init__(self, name, surname="-"):
        self.name = name
        self.surname = surname

    # def to_dict(self):
    #     return {"id": self.id, "name": self.name, "surname": self.surname}
