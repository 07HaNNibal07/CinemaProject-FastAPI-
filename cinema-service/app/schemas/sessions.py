from pydantic import BaseModel,Field,ConfigDict
from typing import Annotated
from datetime import date,time,datetime


class CreateSession(BaseModel):
    movie_name: Annotated[str, Field(...)]
    number_hall: Annotated[int, Field(...)]
    session_date: Annotated[date, Field(...)]
    session_time: Annotated[time, Field(...)]

class InfoAboutSession(BaseModel):
    id:int
    movie_name: Annotated[str, Field(...)]
    number_hall: Annotated[int, Field(...)]
    start_time: Annotated[datetime, Field(...)]
    
    model_config = ConfigDict(from_attributes=True)