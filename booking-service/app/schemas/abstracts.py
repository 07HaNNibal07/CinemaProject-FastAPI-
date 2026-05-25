from pydantic import BaseModel,ConfigDict,Field,field_validator,EmailStr
from pydantic_core import PydanticCustomError
from typing import Annotated
import re
from decimal import Decimal

class AbstractModel(BaseModel):

    name:Annotated[str,Field(...)]
    surname:Annotated[str,Field(...)]
    email:Annotated[EmailStr,Field(...)]
    number:Annotated[str,Field(pattern=r"^(\+7|8)\d{10}$",default= "+79200079902")]
    password:Annotated[str,Field(..., max_length=50)] ='Qwerty_123'
    
    
    @field_validator('password')
    @classmethod
    def validate_password(cls,value):

        if not re.search(r'[A-Z]',value):
            raise ValueError("The password must contain at least one uppercase letter.")
        if not re.search(r'\d',value):
            raise ValueError("The password must contain at least one digit.")
        if not re.search(r'[^A-Za-z0-9]',value):
            raise ValueError("The password must contain at least one symbol")
        
        return value

class AbstractRequest(BaseModel):
    description:Annotated[str,Field(...)]
    status:Annotated[str,Field(...)]
    client_id:Annotated[int,Field(...)]

class AbstractInfoAboutUser(BaseModel):
    id:int
    name:Annotated[str,Field(...)]
    surname:Annotated[str,Field(...)]
    email:Annotated[str,Field(...)]
    number:Annotated[str,Field(...)]
    