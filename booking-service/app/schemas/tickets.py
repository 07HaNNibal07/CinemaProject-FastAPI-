from pydantic import BaseModel,ConfigDict,Field
from typing import Annotated
from decimal import Decimal
from datetime import datetime

class CreateTicket(BaseModel):
    session_id:Annotated[int,Field(...)]
    place_number:Annotated[int,Field(...)]
    
    model_config = ConfigDict(from_attributes=True)
    
class InfoAbotTicket(BaseModel):
    id:int
    session_id:int | None = None
    hall_number:int
    place_number:int
    name_movie:str
    start_time:datetime
    price:Decimal
    client_id:int
    ticket_type:str
    ticket_status:str = 'active'
    model_config = ConfigDict(from_attributes=  True)
    


class ChangePlaceStatus(BaseModel):
    status: str | None = 'booked'

class ChangePlaceDate(BaseModel):
    price:Decimal|None = None
    place_type:str|None = None