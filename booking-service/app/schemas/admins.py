from .abstracts import AbstractModel,AbstractInfoAboutUser,AbstractRequest
from .tickets import InfoAbotTicket
from pydantic import ConfigDict,Field
from typing import Annotated
from decimal import Decimal

class CreateAdmin(AbstractModel):
    
    model_config = ConfigDict(from_attributes=True)


class RequestSchemaForAdmin(AbstractRequest):
    id:Annotated[int,Field(...)]

    model_config = ConfigDict(from_attributes=True)

class InfoAboutClientForAdmin(AbstractInfoAboutUser):
    id:Annotated[int,Field(...)]
    balance:Annotated[Decimal,Field(...)]
    requests:Annotated[list[RequestSchemaForAdmin],Field(...)]
    tickets:Annotated[list[InfoAbotTicket],Field(...)]
    is_active:Annotated[bool,Field(...)]
    
    model_config = ConfigDict(from_attributes = True)