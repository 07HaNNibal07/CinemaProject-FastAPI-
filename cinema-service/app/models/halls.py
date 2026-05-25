from ..core import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import Integer,String,Boolean
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .places import Place
    from .sessions import Session
    
class Hall(Base):
    __tablename__ = 'halls'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    number_hall:Mapped[int] = mapped_column(Integer,unique=True)
    count_place:Mapped[int] = mapped_column(Integer,default=100)
    
    places:Mapped[list['Place']] = relationship(back_populates = 'hall', cascade='all, delete-orphan')

    sessions:Mapped[list['Session']] = relationship(back_populates='hall', cascade='all, delete-orphan')

    