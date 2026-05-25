from sqlalchemy.orm import Mapped,mapped_column,relationship
from ..core.db_dep import Base
from sqlalchemy import String,Boolean,Numeric
from typing import TYPE_CHECKING
from .abstract import BaseModel
if TYPE_CHECKING:
    from .request import RequestModel
    from .tickets import Ticket

class Client(BaseModel):
    __tablename__ = 'clients'

    balance:Mapped[float] = mapped_column(Numeric(10,2))
    
    requests:Mapped[list['RequestModel']] = relationship(
        back_populates='client',
        cascade="all,, delete-orphan"
    )
    tickets:Mapped[list['Ticket']] = relationship(
        back_populates='client',
        cascade= "all, delete-orphan"    
    )