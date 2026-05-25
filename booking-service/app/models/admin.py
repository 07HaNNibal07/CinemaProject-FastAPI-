from ..core import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,Integer,Boolean
from typing import TYPE_CHECKING
from .abstract import BaseModel
if TYPE_CHECKING:
    from .request import RequestModel
    

class Admin(BaseModel):
    __tablename__ = 'admins'
    

    