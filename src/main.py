# now import Base from db.base not db.base_class
from fastapi import FastAPI, Request
import time
from auth.routers import users,admin
from contact.routers import contact
from auth.routers import login
from payment.routers import payment
from payment.routers import transactions
from sms.routers import sms
from sms.routers.tasks import tasks
from auth.routers import forgetPassword
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     print('nigga')
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response

app.include_router(users.router)
app.include_router(admin.router)
app.include_router(login.router)
app.include_router(contact.router)
app.include_router(payment.router)
app.include_router(transactions.router)
app.include_router(sms.router)
app.include_router(tasks.router)
app.include_router(forgetPassword.router)

# @app.get('/')
# async def root():
#     return {'black eyed peas': 'bebot'}
