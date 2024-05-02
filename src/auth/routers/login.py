from fastapi import APIRouter, Depends, HTTPException, status
# from src.auth.schemas import Users
# from auth.schemas import Users
from auth.models import User, UserDetail
from fastapi import FastAPI, Form
from sqlalchemy.orm import Session
import os
# from auth.utils import Authenticate
# from utils import Authenticate
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from database import get_db


from typing import Annotated
from database import SessionLocal
import hashlib


router = APIRouter(
    prefix='/users',
    tags=['users'],
)


class Login(BaseModel):
    email: str
    password: str


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')



ACCESS_TOKEN_EXPIRE_MINUTES = 30

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


class Users(BaseModel):
    id:int
    user_name: str
    email:str
    smsCredit:int
    rate:float
    userRole:str
    class Config:
        from_attributes = True


class Token(BaseModel):
    user: Users
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    id:int|None=None
    userRole:str|None=None


def verify_password(stored_password, provided_password, salt):
    password_hash = hashlib.sha256(
        (provided_password + salt).encode('utf-8')).hexdigest()
    return password_hash == stored_password


# def get_password_hash(password):
#     return pwd_context.hash(password)

# @router.post('/login')
# def login(data: Login, db: Session = Depends(get_db)):
#     email = data.email
#     password = data.password
#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     if not verify_password(user.password, password, "Your Salt"):
#         raise HTTPException(status_code=401, detail="Incorrect password")
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.user_name}, expires_delta=access_token_expires
#     )
#     return Token(access_token=access_token, token_type="bearer")
#     # if username in db:
#     #     user_dict = db[username]
#     #     return UserInDB(**user_dict)


@router.post('/login')
def login(data: Login, db: Session = Depends(get_db)):
    email = data.email
    password = data.password
    user = db.query(User).filter(User.email == email).first()
    if not user.user_detail:
        raise HTTPException(status_code=404, detail="User not found")
    userDetail=db.query(UserDetail).filter(UserDetail.user_id==user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password, password, "Your Salt"):
        raise HTTPException(status_code=401, detail="Incorrect password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name,"id":user.id,"user_type":userDetail.user_type}, expires_delta=access_token_expires
    )
    returnData = Users(id=user.id, user_name=user.user_name,
                     email=user.email,smsCredit=userDetail.sms_credit,rate=userDetail.rate,userRole=userDetail.user_type)
    return Token(user=returnData, access_token=access_token, token_type="bearer")


@router.post('/token')
def login(data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    email = data.username
    password = data.password
    user = db.query(User).filter(User.email == email).first()
    userDetail=db.query(UserDetail).filter(UserDetail.user_id==user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password, password, "Your Salt"):
        raise HTTPException(status_code=401, detail="Incorrect password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name,"id":user.id,"user_type":userDetail.user_type}, expires_delta=access_token_expires
    )
    returnData = Users(id=user.id, user_name=user.user_name,
                       email=user.email,smsCredit=userDetail.sms_credit,rate=userDetail.rate,userRole=userDetail.user_type)
    return Token(user=returnData, access_token=access_token, token_type="bearer")

# def authenticate_user(fake_db, email: str, password: str):
#     user = get_user(fake_db, email)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token_access(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id:str=payload.get('id')
        userRole:str=payload.get('user_type')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username,id=id,userRole=userRole)
    except JWTError:
        raise credentials_exception
    return token_data
    # user = get_user(fake_users_db, username=token_data.username)
    # if user is None:
    #     raise credentials_exception
    # return user


# @app.post("/token")
# async def login_for_access_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
# ) -> Token:
#     user = authenticate_user(
#         fake_users_db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return Token(access_token=access_token, token_type="bearer")
