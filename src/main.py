from fastapi import FastAPI   # now import Base from db.base not db.base_class

from auth.routers import users
from auth.routers import login
app = FastAPI()

app.include_router(users.router)
app.include_router(login.router)


@app.get('/')
async def root():
    return {'black eyed peas':'bebot'}