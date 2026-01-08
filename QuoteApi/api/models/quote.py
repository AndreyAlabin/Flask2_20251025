from api import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
# from api.models.author import AuthorModel


class QuoteModel(db.Model):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(ForeignKey('authors.id'))
    text: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(default='1', server_default='1')
    author: Mapped['AuthorModel'] = relationship(back_populates='quotes') # type: ignore

    def __init__(self, author, text, rating=1):
        self.author = author
        self.text  = text
        self.rating = rating

    def __repr__(self):
        return f'Quote{self.id, self.author}'  
    
    # def to_dict(self):
    #     return {
    #         "quote_id": self.id,
    #         "author": f'id {self.author.id}: {self.author.name} {self.author.surname}',
    #         "text": self.text,
    #         "rating": self.rating
    #     }
