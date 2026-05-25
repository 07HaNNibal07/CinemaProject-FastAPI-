from pydantic_settings import BaseSettings
from pydantic import ConfigDict,BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parents[3]

class DBSettings(BaseModel):

    db_url:str
    db_echo:bool

class AuthJWT(BaseModel):
    private_key_path:Path = BASE_DIR / 'booking-service' / 'app' / 'core' / 'keys' / 'private.key'
    public_key_path:Path = BASE_DIR / 'booking-service' /'app' / 'core' / 'keys' / 'public.key'
    algorithm:str = 'RS256'
    access_token_expire_minutes:int = 15
    refresh_token_expire_days:int = 30
    
    @property
    def private_key(self):
        return self.private_key_path.read_text()
    
    @property
    def public_key(self):
        return self.public_key_path.read_text()


class Settings(BaseSettings):
        
    model_config = {
        'env_file':BASE_DIR/ '.env',
        'env_nested_delimiter':"__",
        'extra':'ignore'
    }
    booking_settings : DBSettings
    auth_jwt : AuthJWT = AuthJWT()

settings = Settings()
