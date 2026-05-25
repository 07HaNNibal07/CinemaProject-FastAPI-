import jwt
from jwt import ExpiredSignatureError,InvalidTokenError
from fastapi import HTTPException,status
from passlib.context import CryptContext
from ..core import settings
from datetime import datetime,timedelta

pwd_context = CryptContext(schemes=['bcrypt'],deprecated = "auto")


def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    return pwd_context.verify(plain_password,hashed_password)



private_key = settings.auth_jwt.private_key
public_key = settings.auth_jwt.public_key

def encode_jwt(
    payload:dict,
    private_key:str = settings.auth_jwt.private_key,
    algorithm:str = settings.auth_jwt.algorithm,
    access_token_expire_minutes:int =settings.auth_jwt.access_token_expire_minutes

):
    to_encode = payload.copy()
    cur_time = datetime.utcnow()
    to_encode.update(exp = cur_time + timedelta(minutes=access_token_expire_minutes))
    return jwt.encode(to_encode,private_key,algorithm=algorithm)


def decode_jwt(
  token:str,
  public_key:str = settings.auth_jwt.public_key,
  algorithm:str = settings.auth_jwt.algorithm  
):
    try:
        return jwt.decode(token, public_key, algorithms=[algorithm])
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

