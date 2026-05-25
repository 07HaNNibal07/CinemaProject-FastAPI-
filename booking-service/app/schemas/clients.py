from pydantic import BaseModel,ConfigDict,Field,field_validator,EmailStr
from pydantic_core import PydanticCustomError
from typing import Annotated
import re
from decimal import Decimal
from .abstracts import AbstractModel,AbstractInfoAboutUser,AbstractRequest
from .tickets import InfoAbotTicket

class CreateClient(AbstractModel):

    balance:Annotated[Decimal,Field(...)]

    model_config = ConfigDict(from_attributes=  True)

class RequestSchema(AbstractRequest):

    model_config = ConfigDict(from_attributes=True)

    
class InfoAboutClient(AbstractInfoAboutUser):
    balance:Annotated[Decimal,Field(...)]
    requests:Annotated[list[RequestSchema],Field(...)]
    tickets:Annotated[list[InfoAbotTicket],Field(...)]
    
    model_config = ConfigDict(from_attributes=  True)




