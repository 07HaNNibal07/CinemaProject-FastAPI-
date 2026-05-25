from contextlib import asynccontextmanager
import logging
import time
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from .routers import client,admin
from .core.auth import router as  login
import httpx


@asynccontextmanager
async def lifespan(app:FastAPI):
    async with httpx.AsyncClient( base_url="http://cinema-service:8000") as client:
        app.state.htttpx_client = client
        yield




app  = FastAPI(lifespan=lifespan)


logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s:  %(asctime)s  -  %(name)s  -  %(message)s')

logger = logging.getLogger('api')




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

app.include_router(router=client)
app.include_router(router=admin)
app.include_router(router=login)





