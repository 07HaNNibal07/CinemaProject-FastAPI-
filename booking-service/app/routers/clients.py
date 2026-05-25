from fastapi import APIRouter,Depends,HTTPException,status,Request

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.clients import Client

from ..schemas.clients import CreateClient,InfoAboutClient,RequestSchema
from ..schemas.tickets import InfoAbotTicket,CreateTicket,ChangePlaceStatus

from ..core.db_dep import current_session
from ..core.auth import require_client

from ..utils.dependencies import get_http_client
from ..utils.cruds import reg_user,cinema_request,BookingService
from ..utils.user_booking_service import UserBooking_Service

import httpx
from decimal import Decimal

from common_auth.redis import redis


router = APIRouter(prefix='/client',tags=['clients'])


@router.post('/register_client',response_model=InfoAboutClient)
async def register_client(
    client_data:CreateClient,
    db:AsyncSession = Depends(current_session)
):
    return await reg_user(Client,client_data,db)


@router.get('/show_my_profile',response_model=InfoAboutClient)
async def show_my_profile(
    client = Depends(require_client),
    get_user:BookingService = Depends(BookingService)
):
    return await get_user.get_info_about_user(client.id)


@router.post('/create_request',response_model=RequestSchema)
async def create_request(
    description:str,
    client = Depends(require_client),
    get_user_request:UserBooking_Service = Depends(UserBooking_Service)
):
    return await get_user_request.get_create_request(client.id,description)


@router.get('/show_hall_sessions',dependencies=[Depends(require_client)])
async def show_hall(
    number_hall:int,
    request:Request,
    client = Depends(get_http_client)
    
):
    return await cinema_request(
        request=request,
        client=client,
        method='get',
        path='/control/show_hall_sessions',
        params={'number_hall':number_hall},
    )


@router.patch('/replenish')
async def replenish(
    money:Decimal,
    db:AsyncSession = Depends(current_session),
    user = Depends(require_client)
):
    user.balance += money
    await db.commit()
    return user.balance


@router.post('/buy_ticket', response_model=InfoAbotTicket)
async def buy_ticket(
    ticket_data:CreateTicket,
    request:Request,
    user = Depends(require_client),
    client = Depends(get_http_client),
    post_buy:UserBooking_Service = Depends(UserBooking_Service)
):
    return await post_buy.post_buy_ticket(
        user_id=user.id,
        request=request,
        client=client,
        ticket_data=ticket_data,
        path='/control/buy_ticket'
    )


    

@router.get('/my_tickets',response_model=list[InfoAbotTicket])
async def my_tickets(
    db:AsyncSession = Depends(current_session),
    user = Depends(require_client)
):
    db_user = await db.scalar(select(Client).options(selectinload(Client.tickets)).where(Client.id==user.id))
    return db_user.tickets
    

@router.delete('/delete_account')
async def delete_accaount(
    request: Request,
    user = Depends(require_client),
    client:httpx.AsyncClient = Depends(get_http_client),
    delete_user:UserBooking_Service = Depends(UserBooking_Service)
):
    return await delete_user.delete_client_account(
        user_id=user.id,
        request=request,
        client=client,
    )


#ТЕСТОВЫЕ ЗАПРОСЫ

@router.get('/all_clients',response_model=list[InfoAboutClient])
async def show_all_clients(db:AsyncSession = Depends(current_session)):
    all_clients = await db.scalars(select(Client).options(selectinload(Client.requests),selectinload(Client.tickets)))
    return all_clients.all()



@router.delete('/delete_all_clients')
async def delete_all_clients(db:AsyncSession = Depends(current_session)):
    clients = await db.scalars(select(Client).options(selectinload(Client.requests),selectinload(Client.tickets)))
    if clients is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    for client in clients:
        await db.delete(client)
        
    await db.commit()
    return {
        'message':"all clients are deleted"
    }


@router.patch('/book_place')
async def  show_pl_ses(
    session_id:int,
    place_number:int,
    status_data:ChangePlaceStatus,
    request:Request,
    client = Depends(get_http_client),
    user = Depends(require_client)
):
    response = await cinema_request(
        request=request,
        client=client,
        method='patch',
        path='/control/change_session_place_status',
        params= {
            "session_id":session_id,
            "place_number":place_number
        },
        json_data=status_data
    )
    key = f"reservation:{session_id}:{place_number}"
    await redis.set(
        key,
        str(user.id),
        ex = 900
    )
    return response

@router.get('/show_session_places',dependencies=[Depends(require_client)])
async def  show_pl_ses(
    session_id:int,
    request:Request,
    client = Depends(get_http_client),
):
    response = await cinema_request(
        request=request,
        client=client,
        method='get',
        path='/control/show_session_places',
        params= {
            "session_id":session_id,
        }
       
    )
    for placec in response:
        owner = await redis.get(f"reservation:{session_id}:{placec['place_number']}")
        if placec['status'] == 'booked' and owner is None:
            await cinema_request(
            request=request,
            client=client,
            method='patch',
            path='/control/change_session_place_ONLYstatus',
            params= {
                "session_id":session_id,
                "place_number":placec['place_number']
            },
            json_data=ChangePlaceStatus(status='available')
        )
            
    updated_response = await cinema_request(
    request=request,
    client=client,
    method='get',
    path='/control/show_session_places',
    params={
        "session_id":session_id,
    }
    )

    return updated_response