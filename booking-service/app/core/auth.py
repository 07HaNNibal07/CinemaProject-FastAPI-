from fastapi import HTTPException,status, APIRouter,Form,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2,OAuth2PasswordBearer
from .db_dep import current_session

from .security import verify_password,encode_jwt,decode_jwt
from sqlalchemy import select,or_
from ..models import Client,Admin



router = APIRouter()

MODELS = {
    Client:'client',
    Admin:'admin',
}



@router.post('/login')
async def login_user(username =Form(...,description='Введите номер или почту'),
                     password = Form(...,description= "Введите пароль"),
                     db:AsyncSession = Depends(current_session)):
    
    for Model in MODELS.keys():
        user = await db.scalar(select(Model).where(Model.is_active.is_(True),or_(Model.email == username,Model.number == username)))
        
        if not user:
            continue
        
        if not verify_password(password,user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        
        role = MODELS.get(Model)
        
        if verify_password(password,user.password):
            payload = {
                'sub': str(user.id),
                'email': user.email,
                'role': role
            }
    
        return {
            'access_token': encode_jwt(payload=payload),
            'token_type':'bearer'
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED
    )
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

def get_model(Model):
    
    async def require_custom(
        token:str = Depends(oauth2_scheme),
        db:AsyncSession = Depends(current_session),
        
    ):
        payload = decode_jwt(token=token)
        user_id = int(payload['sub'])
        user = await db.scalar(select(Model).where(Model.id== user_id, Model.is_active.is_(True)))
        
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        return user
    
    return require_custom

require_client = get_model(Client)
require_admin = get_model(Admin)


    