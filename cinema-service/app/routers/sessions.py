from fastapi import APIRouter,HTTPException,status,Depends
from ..models import Session,Movie,Hall,SessionPlace
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import CreateSession,InfoAboutSession
from ..core import current_session
from datetime import datetime,time,date
from sqlalchemy.orm import selectinload


router = APIRouter(prefix= '/session',tags=['session'])


@router.post('/create_session',response_model= InfoAboutSession)
async def create_session(
    session_data: CreateSession,
    db: AsyncSession = Depends(current_session)
):
    movie = await db.scalar(
        select(Movie).where(Movie.name == session_data.movie_name)
    )
    if not movie:
        raise HTTPException(status_code=404, detail='Movie not found')

    hall = await db.scalar(
        select(Hall)
        .options(selectinload(Hall.places))
        .where(Hall.number_hall == session_data.number_hall)
    )
    if not hall:
        raise HTTPException(status_code=404, detail='Hall not found')
    
    session_time = session_data.session_time.replace(tzinfo=None)

    start_time = datetime.combine(
        session_data.session_date,
        session_time
    )
    
    check_session = await db.scalar(
        select(Session).where(
            Session.number_hall == hall.number_hall,
            Session.start_time == start_time
        )
    )
    if check_session:
        raise HTTPException(status_code=403, detail='Session already exists')

    new_session = Session(
        start_time=start_time,
        number_hall=hall.number_hall,
        movie_name=movie.name
    )

    for place in hall.places:
        new_session.session_places.append(
            SessionPlace(
                place_number=place.number,
                price=place.price,
                place_type=place.place_type,
                status=place.status,
            )
        )

    db.add(new_session)
    await db.commit()
    return new_session

@router.patch('/change_session_datetime',response_model = InfoAboutSession)
async def change_session_datetime(
    session_id:int,
    new_time:time,
    new_date:date,
    db:AsyncSession = Depends(current_session)
):
    session = await db.scalar(select(Session).where(Session.id==session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Session not found'
        )
    start_time = datetime.combine(new_date, new_time.replace(tzinfo=None))
    
    busy_session = await db.scalar(
        select(Session).where(
            Session.number_hall == session.number_hall,
            Session.start_time == start_time,
            Session.id != session_id
        )
    )  
    
    if busy_session:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='date or time is busy')
    
    session.start_time = start_time
    await db.commit()
    return session
    

@router.get('/all_sessions',response_model=list[InfoAboutSession])
async def  all_sessions(
    db:AsyncSession = Depends(current_session)
):
    sessions = await db.scalars(select(Session))
    return sessions.all()

@router.delete('/delete_session')
async def delete_session(
    session_id:int,
    db:AsyncSession = Depends(current_session)
):
    session = await db.scalar(
        select(Session)
        .options(selectinload(Session.session_places))
        .where(Session.id == session_id)
    )
    
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    await db.delete(session)
    await db.commit()
    return {
        'message':'deleted'
    }
    
@router.delete('/delete_all_sessions')
async def delete_all_session(
    db:AsyncSession = Depends(current_session)
):
    sessions = await db.scalars(select(Session).options(selectinload(Session.session_places)))
    for session in sessions:
        await db.delete(session)
    await db.commit()
    return {
        'message':'deleted'
    }
