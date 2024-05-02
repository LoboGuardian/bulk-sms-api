from fastapi import APIRouter, Depends, HTTPException, status
from auth.models import User, UserDetail
from sqlalchemy.orm import Session
from auth.schemas import UserDetails, UsersResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from auth.routers.login import verify_token_access
from database import get_db
from typing import Annotated
from database import SessionLocal
import hashlib
import os

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


def isAdmin(role):
    return True if role == 'Admin' else False


@router.get('/getAllUsers', response_model=list[UsersResponse])
def getAllusers(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    role = verify_token_access(token).userRole
    if not isAdmin(role):
        raise HTTPException(status_code=403, detail="User is not authorized")
    data = db.query(User).join(UserDetail).filter(
        UserDetail.user_type != 'Admin').all()
    
    return data


@router.put('/updateUserDetail/{id}')
def updateUserDetail(data:UserDetails, id:int,token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    role = verify_token_access(token).userRole
    if not isAdmin(role):
        raise HTTPException(status_code=403, detail="User is not authorized")
    userDetail=db.query(UserDetail).filter(UserDetail.user_id==id).one_or_none()
    userDetail.rate=data.rate
    userDetail.sms_credit=data.sms_credit
    db.commit()
    return {'message':"User Details have been updated"}


@router.put('/blockUser/{id}')
def blockUser(id:int,token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    role = verify_token_access(token).userRole
    if not isAdmin(role):
        raise HTTPException(status_code=403, detail="User is not authorized")
    userDetail=db.query(UserDetail).filter(UserDetail.user_id==id).one_or_none()
    userDetail.status=not userDetail.status
    db.commit()
    return {'message':'User has been blocked'} if userDetail.status==False else {'message':'User has been blocked'}

@router.delete(('/deleteUser/{id}'))
def deleteUser(id:int,token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    role = verify_token_access(token).userRole
    if not isAdmin(role):
        raise HTTPException(status_code=403, detail="User is not authorized")
    
    userDetail=db.query(UserDetail).filter(UserDetail.id==id).one_or_none()
    db.delete(userDetail)
    db.commit()
    return {'message':'User deleted'}

