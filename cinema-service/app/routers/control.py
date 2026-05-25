from decimal import Decimal

from common_auth.dependencies import require_client_token,require_admin_token
from fastapi import APIRouter,Depends,HTTPException,status
from ..core import current_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models import Hall,Place,Session,SessionPlace
from ..schemas import (
    InfoAbotPlace,
    CreatePlace,
    InfoAbotHall,
    PatchUpdatePlaces,
    CreateHall,
    InfoAbotHallWithSessions,
    InfoAbotHallWithPlaces,
    InfoAboutSessionPlace,
    PatchSessionPlaceStatus,
    BuyTicketInfo,
)


router = APIRouter(prefix='/control',tags=['control'])


@router.post('/create_hall',response_model=InfoAbotHall)
async def create_hall(
    hall_data:CreateHall,
    place_data:CreatePlace,
    db:AsyncSession = Depends(current_session)
):
    
    db_hall = await db.scalar(select(Hall).where(Hall.number_hall==hall_data.number_hall))
    if db_hall:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Hall is already created')
    
    if hall_data.number_hall == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    hall = Hall(**hall_data.model_dump())
    
    premium_count = int(hall.count_place * 0.2)  
    vip_count = int(hall.count_place * 0.2)     

    
    for number_place in range(1,hall.count_place+1):
        new_place = place_data.model_dump()
        new_place['number'] = number_place
        
        if number_place <= premium_count:
            new_place['place_type'] = 'premium'
            new_place['price'] = 600
        
        elif  number_place <= vip_count+premium_count:
            new_place['place_type'] = 'vip'
            new_place['price'] = 450              
        
        hall.places.append(Place(**new_place))
    
    
    
    db.add(hall)
    await db.commit()
    return await db.scalar(
        select(Hall)
        .options(
            selectinload(Hall.places),
            selectinload(Hall.sessions),
        )
        .where(Hall.id == hall.id)
    )

@router.patch('/change_place',response_model=InfoAbotPlace,dependencies=[Depends(require_admin_token)])
async def change_place(
    number_hall:int,
    place_number:int,
    update_data:PatchUpdatePlaces,
    db:AsyncSession = Depends(current_session)
):
    hall = await db.scalar(select(Hall).options(selectinload(Hall.places)).where(Hall.number_hall==number_hall))
    if not hall:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hall not found"
        )
        
    place = next((i for i in hall.places if i.number == place_number),None)
    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hall not found"
        )

    for key,val in update_data.model_dump(exclude_unset=True).items():
        setattr(place,key,val)
    
    await db.commit()

    return place

@router.patch('/change_session_place_status', response_model=InfoAboutSessionPlace)
async def change_session_place_status(
    session_id: int,
    place_number: int,
    update_data: PatchSessionPlaceStatus,
    db: AsyncSession = Depends(current_session)
):
    session = await db.scalar(
        select(Session)
        .options(selectinload(Session.session_places))
        .where(Session.id == session_id)
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session_place = next(
        (place for place in session.session_places if place.place_number == place_number),
        None
    )
    if not session_place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found"
        )
    if session_place.status == 'booked':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Already booked")
    
    for key, val in update_data.model_dump(exclude_unset=True).items():
        setattr(session_place, key, val)

    await db.commit()
    
    return session_place


@router.patch('/change_session_place_ONLYstatus', response_model=InfoAboutSessionPlace)
async def change_session_place_status(
    session_id: int,
    place_number: int,
    update_data: PatchSessionPlaceStatus,
    db: AsyncSession = Depends(current_session)
):
    session = await db.scalar(
        select(Session)
        .options(selectinload(Session.session_places))
        .where(Session.id == session_id)
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session_place = next(
        (place for place in session.session_places if place.place_number == place_number),
        None
    )
    if not session_place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found"
        )
    
    
    for key, val in update_data.model_dump(exclude_unset=True).items():
        setattr(session_place, key, val)

    await db.commit()
    
    return session_place


@router.patch('/release_ticket', response_model=InfoAboutSessionPlace, dependencies=[Depends(require_client_token)])
async def release_ticket(
    session_id: int,
    place_number: int,
    update_data: PatchSessionPlaceStatus,
    db: AsyncSession = Depends(current_session)
):
    session = await db.scalar(
        select(Session)
        .options(selectinload(Session.session_places))
        .where(Session.id == session_id)
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session_place = next(
        (place for place in session.session_places if place.place_number == place_number),
        None
    )
    if not session_place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found"
        )

    for key, val in update_data.model_dump(exclude_unset=True).items():
        setattr(session_place, key, val)

    session_place = await db.scalar(select(SessionPlace).where(SessionPlace.session_id==session.id))
    session_place.status = 'available'

    await db.commit()
    return session_place


@router.post('/buy_ticket',response_model=BuyTicketInfo,dependencies=[Depends(require_client_token)])
async def buy_ticket(
    session_id:int,
    place_number:int,
    money:Decimal,
    db:AsyncSession = Depends(current_session)
):
    session = await db.scalar(
        select(Session)
        .options(selectinload(Session.session_places))
        .where(Session.id == session_id)
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session_place = next(
        (place for place in session.session_places if place.place_number == place_number),
        None
    )
    if not session_place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found"
        )

    if money < session_place.price:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Not enough money')
    if session_place.status == 'paid':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='This place is already bought')
    session_place.status ='paid'
    
    await db.commit()
    return {
        'session_id': session.id,
        'movie_name': session.movie_name,
        'number_hall': session.number_hall,
        'start_time': session.start_time,
        'place_number': session_place.place_number,
        'price': session_place.price,
        'place_type': session_place.place_type,
        'status': session_place.status,
    }


@router.get('/show_hall_places',response_model=InfoAbotHallWithPlaces)
async def show_hall_places(
    number_hall:int,
    db:AsyncSession = Depends(current_session)
):
    hall = await db.scalar(select(Hall).options(selectinload(Hall.places)).where(Hall.number_hall==number_hall))
    if not hall:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Hall not found")
    return hall

@router.get('/show_session_places', response_model=list[InfoAboutSessionPlace])
async def show_session_places(
    session_id: int,
    db: AsyncSession = Depends(current_session)
):
    session = await db.scalar(
        select(Session)
        .options(selectinload(Session.session_places))
        .where(Session.id == session_id)
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session.session_places


@router.get('/show_hall_sessions',response_model=InfoAbotHallWithSessions)
async def show_hall_sessions(
    number_hall:int,
    db:AsyncSession = Depends(current_session)
):
    hall = await db.scalar(select(Hall).options(selectinload(Hall.sessions)).where(Hall.number_hall==number_hall))
    if not hall:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Hall not found")
    return hall


@router.get('/show_all_halls')
async def show_all_halls(
    db:AsyncSession = Depends(current_session)
):
    all_halls = await db.scalars(select(Hall).options(selectinload(Hall.sessions),selectinload(Hall.places)))
    return all_halls.all()


@router.delete('/delete_hall',dependencies=[Depends(require_admin_token)])
async def delete_hall(
    number_hall:int,
    
    db:AsyncSession = Depends(current_session)
):
    hall = await db.scalar(
        select(Hall)
        .options(
            selectinload(Hall.sessions).selectinload(Session.session_places),
            selectinload(Hall.places),
        )
        .where(Hall.number_hall==number_hall)
    )
    if not hall:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='No such this hall!')

    await db.delete(hall)
    await db.commit()

    return {
        "message":'Success deleted'
    }

@router.delete('/all_delete')
async def all_delete(db:AsyncSession = Depends(current_session)):
    halls = await db.scalars(
        select(Hall).options(
            selectinload(Hall.sessions).selectinload(Session.session_places),
            selectinload(Hall.places),
        )
    )
    for hall in halls:

        await db.delete(hall)
        await db.commit()

    return halls
