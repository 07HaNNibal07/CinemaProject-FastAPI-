from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InfoAboutSessionPlace(BaseModel):
    place_number: int
    price: Decimal
    place_type: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class PatchSessionPlaceStatus(BaseModel):
    status: Optional[str] = None


class BuyTicketInfo(BaseModel):
    session_id: int
    movie_name: str
    number_hall: int
    start_time: datetime
    place_number: int
    price: Decimal
    place_type: str
    status: str

    model_config = ConfigDict(from_attributes=True)
