from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Auth_JWT(BaseSettings):
    public_key_path: Path = BASE_DIR / "keys" / "public.key"
    algorithm: str = "RS256"
    
    @property
    def public_key(self):
        return self.public_key_path.read_text()

class RedisSet(BaseSettings):
    host:str = 'redis'
    port:int = 6379
    decode_responses: bool = True

settings = Auth_JWT()

redis_set = RedisSet()