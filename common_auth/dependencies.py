from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from common_auth.jwt import decode_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def require_client_token(
    token: str = Depends(oauth2_scheme),
):
    payload = decode_jwt(token)

    if payload.get("role") != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only clients allowed",
        )

    return payload


async def require_admin_token(
    token: str = Depends(oauth2_scheme),
):
    payload = decode_jwt(token)

    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins allowed",
        )

    return payload