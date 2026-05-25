from sqlalchemy.orm import Mapped,mapped_column,relationship
from ..core import Base
from sqlalchemy import String,Text,Integer
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .sessions import Session

class Movie(Base):
    __tablename__ = 'movies'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(50),unique=True)
    genre:Mapped[str] = mapped_column(String(50))
    aboutMovie:Mapped[str] = mapped_column(Text)
    age_limit:Mapped[int] = mapped_column(Integer)
    
    sessions:Mapped[list['Session']] = relationship(back_populates='movie')
    
    