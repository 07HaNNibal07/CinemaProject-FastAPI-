from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parents[3]

class DBSettings(BaseModel):
    db_url:str
    db_echo:bool


class Settings(BaseSettings):
    model_config ={
        'env_file': BASE_DIR / '.env',
        'extra':'ignore',
        'env_nested_delimiter':'__'
    }
    
    cinema_settings:DBSettings


settings = Settings()
