from fastapi import Request,HTTPException,status,Depends

from sqlalchemy import select,or_,and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.tickets import CreateTicket, ChangePlaceStatus

from ..models.admin import Admin
from ..models.clients import Client
from ..models.request import RequestModel
from ..models.tickets import Ticket

from ..core import hash_password,current_session

import httpx
from typing import Any
from decimal import Decimal
from datetime import datetime

MODELS = [
    Admin,
    Client
]

async def reg_user(
        Model,
        user,
        db:AsyncSession = Depends(current_session)
    ):
        for model in MODELS:
            check_user = await db.scalar(select(model).where(or_(model.email==user.email,model.number==user.number)))
             
            if check_user:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='This user is already exists')
        
        new_user = user.model_dump()
        new_user['password'] = hash_password(user.password)
        db_user = Model(**new_user)
        db.add(db_user)
        await db.commit()
        if Model is Client:
            return await db.scalar(select(Client)
                .options(
                    selectinload(Client.tickets),
                    selectinload(Client.requests)
                )
                .where(Client.id ==db_user.id)
            )
        elif Model is Admin:
            return await db.scalar(
                select(Admin)
                .where(Admin.id == db_user.id)
            )
    

async def cinema_request(
    request:Request,
    client:httpx.AsyncClient,
    method:str,
    path:str,
    params: dict[str, Any] | None = None,
    json_data:Any = None
):
    token = request.headers.get('authorization')
    headers = {"Authorization": token} if token else {}
    for_json = json_data.model_dump(mode = 'json',exclude_unset = True) if json_data is not None else None
    
    response = await client.request(
            method,
            path,
            params=params,
            json=for_json,
            headers=headers
        )
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=response.status_code,detail=response.json())
    
    return response.json()


async def get_user_request(
    client_id:int,
    request_id:int,
    db:AsyncSession = Depends(current_session)
):
    client = await db.scalar(
        select(Client).options(selectinload(Client.requests)).where(
            and_(Client.id==client_id,Client.is_active.is_(True))
            )
        )
    
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No such client')
    
    request = next((r for r in client.requests if r.id == request_id),None)
    
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No such request')
    return request


class BookingService:
    def __init__(self,db:AsyncSession = Depends(current_session)):
        self.db = db
        
    async def get_info_about_users_for_admin(self):
        clients = await self.db.scalars(select(Client)
                                        .options(
                                            selectinload(Client.tickets),
                                            selectinload(Client.requests)
                                            )
                                        )
        return clients.all()
    
    async def get_info_about_admins_for_admin(self):
        admins = await self.db.scalars(select(Admin)
                                       .where(Admin.is_active.is_(True)
                                              )
                                       )
        return admins.all()
    
    async def get_info_about_user(self,user_id:int):
        user = await self.db.scalar(select(Client)
                                    .options(
                                        selectinload(Client.tickets),
                                        selectinload(Client.requests)
                                    )
                                     .where(Client.id==user_id)
                                     )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No such client')
        
        return user

    async def get_user_request(self,client_id,request_id):
        client = await self.db.scalar(select(Client)
                                      .options(
                                          selectinload(Client.requests)
                                          )
                                      .where((Client.id==client_id)))
    
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No such client')
        
        request = next((r for r in client.requests if r.id == request_id),None)
        
        if not request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No such request')
    
        return request
    
    async def get_user_requests(self,client_id):
        client = await self.db.scalar(select(Client)
                                       .options(
                                           selectinload(Client.requests)
                                       )
                                       .where(Client.id == client_id)
                                    )
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No such client')
        
        return client.requests
    
    async def get_user_ticket(self,client_id,tickets_id):
        client = await self.db.scalar(select(Client)
                                      .options(
                                          selectinload(Client.tickets)
                                          )
                                      .where((Client.id==client_id)))
        
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No such client')
        
        ticket = next((r for r in client.tickets if r.id == tickets_id),None)
        
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No such tickets')
        
        return ticket
    
    async def get_user_tickets(self,user_id):
        
        client = await self.db.scalar(select(Client).options(selectinload(Client.tickets)).where(Client.id==user_id))
        
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No such client')
        
        return client.tickets
    
    async def get_change_user_ticket(self,
                                     user_id,
                                     session_id,
                                     place_number,
                                     request,
                                     client,
                                     update_data
                                     ):
        db_user = await self.db.scalar(
        select(Client).options(selectinload(Client.tickets)).where(Client.id == user_id)
        )
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No such client'
            )

        ticket = next(
            (
                t for t in db_user.tickets
                if t.ticket_status != 'canceled'
                and t.session_id == session_id
                and t.place_number == place_number
            ),None
        )
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Ticket not found'
            )

        place =  await cinema_request(
            request=request,
            client=client,
            method='patch',
            path = '/control/change_session_place_status',
            params={
                'session_id':session_id,
                'place_number':place_number
                },
            json_data=update_data,
        )

        ticket.ticket_status = 'canceled'

        back_money = Decimal(str(place['price']))
        db_user.balance += back_money

        await self.db.commit()
        return {
            'message':'ready'
        }
