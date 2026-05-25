from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core import Base

if TYPE_CHECKING:
    from .sessions import Session


class SessionPlace(Base):
    __tablename__ = "session_places"
    __table_args__ = (UniqueConstraint("session_id", "place_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    place_number: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    place_type: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="available")

    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    session: Mapped["Session"] = relationship(back_populates="session_places")
