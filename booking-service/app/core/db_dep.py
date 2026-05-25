from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from .config import settings

class Base(DeclarativeBase):
    pass



engine = create_async_engine(settings.booking_settings.db_url,echo=settings.booking_settings.db_echo)

session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_= AsyncSession

)

async def current_session():
    async with session() as db:
        yield db