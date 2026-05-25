from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine,async_sessionmaker
from .config import settings

class Base(DeclarativeBase):
    pass



engine = create_async_engine(settings.cinema_settings.db_url)

session = async_sessionmaker(
    bind = engine,
    expire_on_commit = False,
    class_ = AsyncSession
)

async def current_session():
    async with session() as db:
        yield db