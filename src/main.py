from fastapi import FastAPI   # now import Base from db.base not db.base_class

from auth.routers import users
from auth.routers import login
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(login.router)


@app.get('/')
async def root():
    return {'black eyed peas':'bebot'}