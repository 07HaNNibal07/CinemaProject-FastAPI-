from fastapi import APIRouter,Depends,Request

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.auth import current_session,require_admin

from ..models.admin import Admin

from ..schemas.tickets import InfoAbotTicket,ChangePlaceStatus,ChangePlaceDate
from ..schemas.admins import CreateAdmin,InfoAboutClientForAdmin
from ..schemas.abstracts import AbstractInfoAboutUser

from ..utils.dependencies import get_http_client
from ..utils.cruds import reg_user,BookingService,cinema_request

import httpx


router = APIRouter(prefix='/admin',tags=['admins'])


@router.get('/all_admins',response_model = list[AbstractInfoAboutUser])
async def show_all_admins(
    get_admins:BookingService = Depends(BookingService)
):
    return await get_admins.get_info_about_admins_for_admin()


@router.post('/create_admin',response_model=AbstractInfoAboutUser)
async def create_admin(
    admin_data:CreateAdmin,
    db:AsyncSession = Depends(current_session)
):
    return await reg_user(Admin,admin_data,db)


@router.get('/show_all_clients',response_model=list[InfoAboutClientForAdmin],dependencies=[Depends(require_admin)])
async def show_all_requests(
    get_clients:BookingService = Depends(BookingService)
):
    return await get_clients.get_info_about_users_for_admin()


@router.get('/show_client',response_model=InfoAboutClientForAdmin,dependencies= [Depends(require_admin)])
async def show_client(
    client_id:int,
    get_client:BookingService = Depends(BookingService)
):
    return await get_client.get_info_about_user(client_id)


@router.get('/user_request',dependencies=[Depends(require_admin)])
async def show_user_request(
    client_id:int,
    request_id:int,
    get_request:BookingService = Depends(BookingService)
):
    return await get_request.get_user_request(client_id,request_id)


@router.get('/user_requests',dependencies=[Depends(require_admin)])
async def show_user_requests(
    client_id:int,
    get_requests:BookingService = Depends(BookingService)
):
    return await get_requests.get_user_requests(client_id)


@router.get('/user_ticket',response_model = InfoAbotTicket,dependencies=[Depends(require_admin)])
async def user_ticket(
    user_id:int,
    tickets_id:int,
    get_ticket:BookingService = Depends(BookingService)
):
    return await get_ticket.get_user_ticket(user_id,tickets_id)
    

@router.get('/user_tickets',response_model=list[InfoAbotTicket],dependencies=[Depends(require_admin)])
async def user_tickets(
    user_id:int,
    get_tickets:BookingService = Depends(BookingService)
):
    return await get_tickets.get_user_tickets(user_id)


@router.patch('/change_user_ticket', dependencies=[Depends(require_admin)])
async def change_user_ticket(
    request: Request,
    user_id: int,
    session_id: int,
    place_number: int,
    update_data: ChangePlaceStatus,
    client:httpx.AsyncClient = Depends(get_http_client),
    get_changes:BookingService = Depends(BookingService),
):
    return await get_changes.get_change_user_ticket(
        user_id,
        session_id,
        place_number,
        request,
        client,
        update_data
    )
    

@router.patch('/change_place',dependencies=[Depends(require_admin)])
async def change_place(
    request:Request,
    number_hall:int,
    number_place:int,
    replace_data:ChangePlaceDate,
    client:httpx.AsyncClient = Depends(get_http_client)
):
    return await cinema_request(
        request=request,
        client=client,
        method='patch',
        path='/control/change_place',
        params={
            'number_hall':number_hall,
            'place_number':number_place,
        },
        json_data=replace_data,
    )
    

@router.delete('/delete_hall',dependencies=[Depends(require_admin)])
async def delete_hall(
    request:Request,
    hall_number:int,
    client = Depends(get_http_client)
):
    return await cinema_request(
        request = request,
        client = client,
        method = 'delete',
        path = '/control/delete_hall',
        params = {
            'number_hall':hall_number
            },
        )
    

