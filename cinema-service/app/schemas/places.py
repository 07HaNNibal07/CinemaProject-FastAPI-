from pydantic import BaseModel,ConfigDict
from decimal import Decimal
from typing import Optional

class CreatePlace(BaseModel):
    price:Decimal = 300
    status:str = "available"
    place_type:str ='standard'
    number:int

    model_config = ConfigDict(from_attributes=True)
    
class InfoAbotPlace(BaseModel):
    number:int
    price:Decimal
    status:str
    place_type:str
    
    model_config = ConfigDict(from_attributes=True)

class PatchUpdatePlaces(BaseModel):
    price:Optional[Decimal] = None
    status:Optional[str] = None
    place_type:Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)