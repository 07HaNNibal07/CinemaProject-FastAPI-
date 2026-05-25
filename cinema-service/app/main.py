from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from .routers import control,movie,session
import logging
import time
from contextlib import asynccontextmanager
from common_auth.redis import redis
import asyncio
from .utils import listen_expired

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s:  %(asctime)s - %(name)s  -  %(message)s')

logger = logging.getLogger('api')




@asynccontextmanager
async def lifespan(app:FastAPI):
    task = asyncio.create_task(listen_expired())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)





@app.middleware("http")
async def log_all(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        duration = int((time.time() - start) * 1000)

        if response.status_code>=500:
            log_func = logger.error
        elif response.status_code>=400:
            log_func = logger.warning
        else:
            log_func = logger.info
                
        log_func(f"{request.client.host} - {request.method} {request.url.path} - {response.status_code} - {duration}ms")
        
        return response

    except Exception as e:
        duration = int((time.time() - start) * 1000)
        logger.error(
            f"{request.client.host} - {request.method} {request.url.path} - CRASH - {duration}ms - {e}"
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Server error"}
        )


app.include_router(control)
app.include_router(movie)
app.include_router(session)
