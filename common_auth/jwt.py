import jwt
from jwt import ExpiredSignatureError,InvalidTokenError
from fastapi import HTTPException,status
from .config import settings

def decode_jwt(
  token:str,
  public_key:str = settings.public_key,
  algorithm:str = settings.algorithm  
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

