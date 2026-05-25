from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import ForeignKey,Numeric
from ..core import Base
from decimal import Decimal
from typing import TYPE_CHECKING
from datetime import datetime
if TYPE_CHECKING:
    from .clients import Client

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    session_id:Mapped[int | None] = mapped_column(nullable=True)
    hall_number:Mapped[int] = mapped_column()
    place_number:Mapped[int] = mapped_column()
    name_movie:Mapped[str] = mapped_column()
    start_time:Mapped[datetime] = mapped_column()
    ticket_type:Mapped[str] = mapped_column()
    ticket_status:Mapped[str] = mapped_column(default='active')
    price:Mapped[Decimal] = mapped_column(Numeric(10,2))
    client_id:Mapped[int] = mapped_column(ForeignKey('clients.id'))
    
    client:Mapped['Client'] = relationship(back_populates='tickets')
    
