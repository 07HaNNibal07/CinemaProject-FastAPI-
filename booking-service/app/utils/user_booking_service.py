from fastapi import Depends,Request,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from ..core import current_session
import httpx
from ..models.clients import Client
from ..models.tickets import Ticket
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from .cruds import cinema_request
from ..schemas.tickets import ChangePlaceStatus,CreateTicket
from decimal import Decimal
from datetime import datetime
from ..models.request import RequestModel
from common_auth.redis import redis
from ..tasks import send_ticket_notification

class UserBooking_Service:
    def __init__(self,db:AsyncSession = Depends(current_session)):
        self.db = db
        
    async def delete_client_account(
        self,
        user_id: int,
        request: Request,
        client: httpx.AsyncClient,
    ):
        db_client = await self.db.scalar(
            select(Client)
            .options(
                selectinload(Client.requests),
                selectinload(Client.tickets),
            )
            .where(Client.id == user_id, Client.is_active.is_(True))
        )

        if not db_client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        for user_request in db_client.requests:
            user_request.status = 'canceled'

        for ticket in db_client.tickets:
            if ticket.ticket_status == 'canceled':
                continue

            if ticket.session_id is not None:
                await cinema_request(
                    request=request,
                    client=client,
                    method='patch',
                    path='/control/release_ticket',
                    params={
                        'session_id': ticket.session_id,
                        'place_number': ticket.place_number,
                    },
                    json_data=ChangePlaceStatus(status='available'),
                )

            ticket.ticket_status = 'canceled'
            db_client.balance += ticket.price

        db_client.is_active = False

        await self.db.commit()
        return {'message': 'account deactivated'}
    
    async def post_buy_ticket(self,
                              user_id:int,
                              request:Request,
                              client:httpx.AsyncClient,
                              ticket_data:CreateTicket,
                              path:str):
        db_client = await self.db.scalar(select(Client)
                                         .options(
                                             selectinload(Client.tickets)
                                             )
                                         .where(Client.id == user_id)
                                        )
        if not db_client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such client')

        owner = await redis.get(f"reservation:{ticket_data.session_id}:{ticket_data.place_number}")
        
        
        
        if owner is not None and int(owner) != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="This reservation belongs to another user")
        else:
            await redis.delete(f"reservation:{ticket_data.session_id}:{ticket_data.place_number}")
            
        
        place_data  = await cinema_request(
            request=request,
            client=client,
            method='post',
            path=path,
            params={
                    'session_id':ticket_data.session_id,
                    'place_number':ticket_data.place_number,
                    'money':str(db_client.balance)
                    },
            )

        
        ticket_price = Decimal(str(place_data['price']))
        
        ticket = Ticket(
            session_id=place_data['session_id'],
            hall_number=place_data['number_hall'],
            place_number=place_data['place_number'],
            name_movie=place_data['movie_name'],
            start_time=datetime.fromisoformat(place_data['start_time']),
            ticket_type=place_data['place_type'],
            ticket_status='active',
            price=ticket_price,
        )

        db_client.tickets.append(ticket)
        db_client.balance -= ticket_price
            
        await self.db.commit()

        send_ticket_notification.delay(
        user_id,
        ticket_data.session_id,
        ticket_data.place_number,
    )
        
        return ticket


    
    
    async def get_create_request(self,
                                 user_id:int,
                                 description:str,
                                 ):
        
        db_client = await self.db.scalar(select(Client).options(selectinload(Client.requests),selectinload(Client.tickets)).where(Client.id==user_id))
        
        new_request = RequestModel(description = description,status = 'active')
        db_client.requests.append(new_request)
        
        await self.db.commit()

        return new_request
