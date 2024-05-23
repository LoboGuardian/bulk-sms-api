from fastapi import APIRouter, Depends, HTTPException, status
from auth.models import User, UserDetail
from sqlalchemy.orm import Session
from auth.schemas import GetAllUsersResponse, SaveSettingData, UserDetails, UsersResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from auth.routers.login import verify_token_access
from payment.models import PaymentMode
from database import get_db
from typing import Annotated, Union
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


@router.get('/getAllUsers/{pageNumber}', response_model=GetAllUsersResponse)
def getAllusers(pageNumber:int,token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    role = verify_token_access(token).userRole
    if not isAdmin(role):
        raise HTTPException(status_code=403, detail="User is not authorized")
    data = db.query(User).join(UserDetail).filter(
        UserDetail.user_type != 'Admin').limit(5).offset((pageNumber-1)*5)
    count = db.query(User).join(UserDetail).filter(
        UserDetail.user_type != 'Admin').count()
    totalCount = 0
    if count == 5:
        totalCount = 1
    else:
        if count % 5 == 0:
            totalCount = count/5
        else:
            totalCount = (count//5)+1
    return {'count':totalCount,'data': data}
    # return data


@router.put('/updateUserDetail/{id}')
def updateUserDetail(data: UserDetails, id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    role = verify_token_access(token).userRole
    if not isAdmin(role):
        raise HTTPException(status_code=403, detail="User is not authorized")
    userDetail = db.query(UserDetail).filter(
        UserDetail.user_id == id).one_or_none()
    userDetail.rate = data.rate
    userDetail.sms_credit = data.sms_credit
    db.commit()
    return {'message': "User Details have been updated"}


@router.put('/blockUser/{id}')
def blockUser(id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    role = verify_token_access(token).userRole
    if not isAdmin(role):
        raise HTTPException(status_code=403, detail="User is not authorized")
    userDetail = db.query(UserDetail).filter(
        UserDetail.user_id == id).one_or_none()
    userDetail.status = not userDetail.status
    db.commit()
    return {'message': 'User has been blocked'} if userDetail.status == False else {'message': 'User has been blocked'}


@router.delete(('/deleteUser/{id}'))
def deleteUser(id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    role = verify_token_access(token).userRole
    if not isAdmin(role):
        raise HTTPException(status_code=403, detail="User is not authorized")

    userDetail = db.query(UserDetail).filter(UserDetail.id == id).one_or_none()
    db.delete(userDetail)
    db.commit()
    return {'message': 'User deleted'}


@router.get('/settings')
def getSetting(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    role = verify_token_access(token).userRole
    if not isAdmin(role):
        raise HTTPException(status_code=403, detail="User is not authorized")
    Esewa = db.query(PaymentMode).filter(PaymentMode.provider ==
                                         'E-sewa', PaymentMode.environment == 'production').first()
    Khalti = db.query(PaymentMode).filter(PaymentMode.provider ==
                                          'Khalti', PaymentMode.environment == 'production').first()
    return {'Esewa': Esewa.value, 'Khalti': Khalti.value}



@router.post('/settings')
def saveSetting(data: SaveSettingData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    role = verify_token_access(token).userRole
    if not isAdmin(role):
        raise HTTPException(status_code=403, detail="User is not authorized")
    Esewa = db.query(PaymentMode).filter(PaymentMode.provider ==
                                         'E-sewa', PaymentMode.environment == 'production').first()
    Khalti = db.query(PaymentMode).filter(PaymentMode.provider ==
                                          'Khalti', PaymentMode.environment == 'production').first()
    if data.esewa_token:
        Esewa.value = data.esewa_token
    if data.khalti_token:
        Khalti.value = data.khalti_token

    db.commit()
    return {'message': 'Settings have been updated'}


@router.post('/')
def EditAdminData():
    pass
