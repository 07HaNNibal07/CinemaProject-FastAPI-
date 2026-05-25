from ..core import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import String,Integer,Boolean


class BaseModel(Base):
    __abstract__ =True
    
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(50))
    surname:Mapped[str] = mapped_column(String(50))
    email:Mapped[str] = mapped_column(String(50),unique=True)
    number:Mapped[str] = mapped_column(String(50),unique=True)
    password:Mapped[str] = mapped_column(String(255))
    is_active:Mapped[bool] = mapped_column(Boolean,default=True)
    