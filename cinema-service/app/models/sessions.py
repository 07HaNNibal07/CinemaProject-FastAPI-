from sqlalchemy.orm import Mapped,mapped_column,relationship
from ..core import Base
from sqlalchemy import String,Text,DateTime,UniqueConstraint,ForeignKey
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .halls import Hall
    from .movies import Movie
    from .session_places import SessionPlace

class Session(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        UniqueConstraint('number_hall','start_time'),
    )
    
    id:Mapped[int] = mapped_column(primary_key=True)
    start_time:Mapped[datetime] = mapped_column(DateTime)
    number_hall:Mapped[int] = mapped_column(ForeignKey('halls.number_hall'))
    movie_name: Mapped[str] = mapped_column(ForeignKey('movies.name'))
    
    hall:Mapped['Hall'] = relationship(back_populates='sessions')
    movie:Mapped['Movie']= relationship(back_populates='sessions')
    session_places: Mapped[list['SessionPlace']] = relationship(
        back_populates='session',
        cascade='all, delete-orphan'
    )
