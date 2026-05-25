from pydantic import BaseModel,ConfigDict
from .places import InfoAbotPlace
from .sessions import InfoAboutSession

class CreateHall(BaseModel):
    number_hall: int = 1
    count_place: int = 100

class InfoAbotHall(BaseModel):
    number_hall:int
    count_place:int
    sessions:list[InfoAboutSession]
    places:list[InfoAbotPlace]
    
    model_config = ConfigDict(from_attributes=True)
    
class InfoAbotHallWithSessions(BaseModel):
    sessions: list[InfoAboutSession]

    model_config = ConfigDict(from_attributes=True)

class InfoAbotHallWithPlaces(BaseModel):
    places: list[InfoAbotPlace]

    model_config = ConfigDict(from_attributes=True)