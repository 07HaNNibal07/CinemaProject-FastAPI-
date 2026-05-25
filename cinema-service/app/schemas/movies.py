from pydantic import BaseModel,Field,ConfigDict
from typing import Annotated,Optional


class MovieSchema(BaseModel):
    
    name:Annotated[str,Field(...)]
    genre:Annotated[str,Field(...)]
    aboutMovie:Annotated[str,Field(...)]
    age_limit:Annotated[int,Field(...)]
    
    model_config = ConfigDict(from_attributes=True)


class InfoAboutMovie(MovieSchema):
    id:Annotated[int,Field(...)]
    
    model_config = ConfigDict(from_attributes=True)

class PatchMovie(BaseModel):
    name:Annotated[str |None,Field(...)] = None
    genre:Annotated[str |None,Field(...)] = None
    aboutMovie:Annotated[str |None,Field(...)] = None
    age_limit:Annotated[int |None,Field(...)] = None