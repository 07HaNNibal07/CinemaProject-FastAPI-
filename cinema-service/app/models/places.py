from ..core import Base
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey,Numeric,String,UniqueConstraint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .halls import Hall


class Place(Base):
    __tablename__ = 'places'
    __table_args__ = (UniqueConstraint('hall_id','number'),)
    
    id:Mapped[int] = mapped_column(primary_key=True)
    price:Mapped[float] = mapped_column(Numeric(10,2))
    status:Mapped[str] = mapped_column(String)
    place_type:Mapped[str] = mapped_column(String)
    number:Mapped[int] = mapped_column(nullable=False)
    
    hall_id:Mapped[int] = mapped_column(ForeignKey('halls.id'))
    hall:Mapped['Hall'] = relationship(back_populates="places")
    
    
