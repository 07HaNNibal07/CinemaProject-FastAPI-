from fastapi import APIRouter,HTTPException,status,Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import MovieSchema,InfoAboutMovie,PatchMovie
from ..core import current_session
from common_auth.dependencies import require_admin_token,require_client_token
from ..models import Movie

router = APIRouter(prefix='/movies',tags=['movies'])

@router.post('/create_movie',response_model=MovieSchema)
async def create_movie(
    movie_data:MovieSchema,
    db:AsyncSession = Depends(current_session),
):
    movie = await db.scalar(select(Movie).where(Movie.name == movie_data.name))
    if movie:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='The movie is already created')
    
    new_movie = Movie(**movie_data.model_dump())
    db.add(new_movie)
    await db.commit()
    
    return new_movie
    
@router.get('/all_movie',response_model=list[InfoAboutMovie])
async def all_movie(
    db:AsyncSession = Depends(current_session)
):
    movies = await db.scalars(select(Movie))
    return movies.all()

@router.get('/movie',response_model=InfoAboutMovie)
async def movie(
    movie_name:str,
    db:AsyncSession = Depends(current_session)
):
    movie = await db.scalar(select(Movie).where(Movie.name==movie_name))
    return movie

@router.patch('/change_movie_data',response_model=InfoAboutMovie)
async def change_movie_data(
    movie_id:int,
    movie_data:PatchMovie,
    db:AsyncSession = Depends(current_session)
):
    movie = await db.scalar(select(Movie).where(Movie.id==movie_id))
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    new_data = movie_data.model_dump(exclude_unset=True)
    for key,val in new_data.items():
        setattr(movie,key,val)
    
    await db.commit()
    
    return movie

@router.delete('/delete_movie')
async def delete_movie(
    movie_name:str,
    db:AsyncSession = Depends(current_session)
):
    movie = await db.scalar(select(Movie).where(Movie.name==movie_name))
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(movie)
    await db.commit()
    return {"message":'deleted'}



# Movie(
#     name="Interstellar",
#     genre="Sci-Fi",
#     aboutMovie="""
# A team of astronauts travels through a wormhole in search of a new home for humanity after Earth begins to collapse from environmental disasters. 
# The mission forces them to face impossible choices involving time, sacrifice, and survival.
# """,
#     age_limit="16+"
# )

# Movie(
#     name="Blade Runner 2049",
#     genre="Cyberpunk",
#     aboutMovie="""
# A young blade runner discovers a secret capable of plunging society into chaos. 
# His investigation leads him to a former blade runner who vanished decades ago.
# """,
#     age_limit="18+"
# )