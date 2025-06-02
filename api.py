from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Dict, List
import time
import asyncio
from gemini import get_movie_recommendation
from schema import Payload, Movie_Response
import logging


logging.basicConfig(filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Store request timestamps per IP
request_logs: Dict[str, List[float]] = {}
# Store blocked IPs with unblock timestamps
blocked_ips: Dict[str, float] = {}

# Lock to manage concurrent access
lock = asyncio.Lock()

RATE_LIMIT = 10         # max requests
RATE_PERIOD = 60        # per 60 seconds
BLOCK_DURATION = 4 * 60 # block for 4 minutes


async def rate_limiter(request: Request):
    client_ip = request.client.host
    now = time.time()

    async with lock:
        # Unblock IP if block time has passed
        if client_ip in blocked_ips:
            if now >= blocked_ips[client_ip]:
                del blocked_ips[client_ip]
                request_logs.pop(client_ip, None)
            else:
                return False

        # Get timestamps for this IP
        timestamps = request_logs.get(client_ip, [])
        # Filter out timestamps older than RATE_PERIOD
        timestamps = [ts for ts in timestamps if now - ts < RATE_PERIOD]
        timestamps.append(now)
        request_logs[client_ip] = timestamps

        if len(timestamps) > RATE_LIMIT:
            # Block the IP
            blocked_ips[client_ip] = now + BLOCK_DURATION
            return False

    return True


# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     start_time = time.time()
#     logging.info(f"Incoming request: {request.method} {request.url.path}")
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     logging.info(f"Response status: {response.status_code}, Process time: {process_time:.4f}s")
#     print(f"Response status: {response.status_code}, Process time: {process_time:.4f}s")


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     return JSONResponse(
#         status_code=422,
#         content={"detail": "Invalid schema provided. Expected fields: name (str), id (int)."}
#     )

@app.post("/get-movie", response_model=Movie_Response)
async def get_movie(payload: Payload = Depends(), request: Request = None):
    print(blocked_ips)
    allowed = await rate_limiter(request)
    if not allowed:
        return Response(status_code=429)

    try:
        response = await get_movie_recommendation(payload)
        if response is not False:
            return response
        else:
            logging.error(f"Error in get_data: get_movie_recommendation function returned false")
            # raise HTTPException(status_code=500, detail="Internal Server Error")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    except Exception as e:

        print(e)
        logging.error(f"Error in get_data: {e}")

        raise HTTPException(status_code=500, detail="Internal Server Error")
    
