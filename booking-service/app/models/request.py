from ..core import Base
from sqlalchemy import String,Text,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .clients import Client


class RequestModel(Base):
    __tablename__ = 'requests'
    
    id:Mapped[int] = mapped_column(primary_key=True)
    description:Mapped[str] = mapped_column(Text)
    status:Mapped[str] = mapped_column(String(20))
    
    client_id:Mapped[int] = mapped_column(ForeignKey('clients.id'))
    
    client:Mapped['Client'] = relationship(back_populates='requests')
    
    