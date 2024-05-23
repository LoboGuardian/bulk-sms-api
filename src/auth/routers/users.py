from datetime import datetime, timedelta, timezone
import os
from fastapi import APIRouter, Depends, HTTPException, Query, status
# from src.auth.schemas import Users
from auth.schemas import UpdateUser, Users, UserDetailResponse
from auth.models import User, UserDetail, UserToken
from fastapi import FastAPI, Form
from jose import JWTError, jwt
# from auth.utils import Authenticate
from pydantic import BaseModel, EmailStr, Field, validator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contact.models import ContactGroup
from auth.routers.login import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, verify_password, verify_token_access
from auth.schemas import ChangePassword
# from utils import Authenticate
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from utils import has_only_english_characters
from typing import Annotated, Union
from database import get_db
import re
from database import SessionLocal
import hashlib
import random
import string
from auth.routers.admin import isAdmin

router = APIRouter(
    prefix='/users',
    tags=['users'],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

PUBLIC_SECRET_KEY = os.getenv('PUBLIC_SECRET_KEY')

PUBLIC_ALGORITHM = os.getenv('PUBLIC_ALGORITHM')



class TokenData(BaseModel):
    username: str | None = None
    id: int | None = None
    userRole: str | None = None



class EnglishString(str):
    # Regular expression to match English alphabets and spaces
    pattern = re.compile(r'^[a-zA-Z\s]+$')

    def __init__(self, value):
        if not self.pattern.match(value):
            raise ValueError("Value must be an English string")
        super().__init__(value)


def has_white_spaces(text):
    return any(char.isspace() for char in text)


class UserRegistration(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    username: str = Field(...,
                          description="The username", min_length=1, max_length=15)
    email: EmailStr = Field(..., description="The email address")
    phone_number: str = Field(..., description="The phone number",
                              min_length=10, max_length=13)
    company_name: str = Field(..., description='The company name')
    company_address: str = Field(..., description='The company address')

    password: str = Field(..., description="The password",
                          min_length=6, max_length=15)

    @validator('username')
    def validate_username(cls, v):
        if not has_only_english_characters(v):
            if has_white_spaces(v):
                raise ValueError(
                    "Username must contain only letters no white sapce")
            raise ValueError("Username must contain only letters ")
        return v


@router.get("/root/", tags=["users"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


# auth_service = Authenticate()

def email_exists(email, db: Session):
    # Query the database for the email
    user = db.query(User).filter(User.email == email).first()
    return user is not None


uppercase_pattern = re.compile(r"[A-Z]")
special_character_pattern = re.compile(r"[@$!%*?&]")
digit_pattern = re.compile(r"\d")


class PasswordResponse(BaseModel):
    valid: bool
    criteria_not_met: list[str] = []


def validate_password(password: str):
    not_met_criteria = []
    if not uppercase_pattern.search(password):
        not_met_criteria.append("uppercase")
    if not special_character_pattern.search(password):
        not_met_criteria.append("special character")
    if not digit_pattern.search(password):
        not_met_criteria.append("digit")
    if len(not_met_criteria) > 0:
        return JSONResponse(
            status_code=400,
            # content={"valid": False, "criteria_not_met": not_met_criteria}
            content={"detail": [{
                "type": "value_error",
                "loc": [
                    "body",
                    "new_password"
                ],
                "msg": f"Value is not a valid password: The password is not valid. It must have {not_met_criteria[0]}",
                "input": password,
                "ctx": {
                    "reason": "The email address is not valid. It must have exactly one @-sign."
                }}]
            }
        )
    else:
        return True


@router.post("/register/", tags=['users'])
async def register_user(data: UserRegistration, db: Session = Depends(get_db)):
    # print(data)
    username = data.username
    email = data.email
    password = data.password
    phone_number = data.phone_number
    company_name = data.company_name
    company_address = data.company_address

    db = SessionLocal()

    salt = "Your Salt"
    if validate_password(password):
        if validate_password(password) != True:
            return validate_password(password)
        password_hash = hashlib.sha256(
            (password + salt).encode('utf-8')).hexdigest()
        # print(password_hash)
        try:
            # Create a new user instance
            new_user = User(user_name=username,
                            password=password_hash, email=email, phone_number=phone_number, company_address=company_address, company_name=company_name)
            # print(new_user)
            if email_exists(email, db):
                return JSONResponse(
                    status_code=500,
                    content={
                        "email": "User already exists with this email address"},
                )
            # Add user to the database
            else:
                # print('here')
                db.add(new_user)
                # Commit the transaction
                db.flush()
                db.commit()
                # Refresh the user instance to access its generated id
                db.refresh(new_user)
                print(new_user.id)
                savableData = UserDetail(
                    user_id=new_user.id, user_type='Client', sms_credit=0, rate=1, status=True)
                db.add(savableData)
                db.commit()
                db.refresh(savableData)
                savableToken=UserToken(userDetailId=savableData.id,token=generate_unique_random_string())
                db.add(savableToken)
                new_contact_group = ContactGroup(
                    title='Unassigned', user_id=new_user.id)
                db.add(new_contact_group)
                db.commit()
            return {"message": "User registered successfully", "user_id": new_user.id}
        except Exception as e:
            # Rollback the transaction in case of any error
            db.rollback()
            raise HTTPException(
                status_code=500, detail=f"An error occurred: {e}")
        finally:
            # Close the database session
            db.close()




@router.put('/updateUserDetails')
def updateUserDetails(userId: Union[int, None], data: UpdateUser, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    id = verify_token_access(token).id
    if(userId):
        role=verify_token_access(token).userRole
        if not isAdmin(role):
            raise HTTPException(status_code=403, detail="User is not authorized")
        else:
            user = db.query(User).filter(User.id == userId).first()
    else:
        user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any([data.user_name, data.email, data.company_name, data.company_address, data.phone_number]):
        return {"message": "No data provided to update"}
    if data.user_name:
        user.user_name = data.user_name
    if data.email:
        user.email = data.email
    if data.company_name:
        user.company_name = data.company_name
    if data.company_address:
        user.company_address = data.company_address
    if data.phone_number:
        user.phone_number = data.phone_number

    db.commit()
    return {"message": "User details updated successfully",'name':data.user_name}


@router.get('/getUserDetail/{id}', tags=['users'], response_model=UserDetailResponse)
async def getUserDetail(id: int, db: Session = Depends(get_db)):
    data = db.query(UserDetail).filter(UserDetail.user_id == id).one_or_none()
    db.close()
    return data


@router.put('/changePassword')
def changePassword(data: ChangePassword, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    id = verify_token_access(token).id
    user = db.query(User).filter(User.id == id).first()
    salt = "Your Salt"
    if not verify_password(user.password, data.current_password, "Your Salt"):
        raise HTTPException(status_code=400, detail=[{
            "type": "value_error",
            "loc": [
                    "body",
                    "current_password"
            ],
            "msg": f"Current password is incorrect",
            "input": user.password,
            "ctx": {
                "reason": "The email address is not valid. It must have exactly one @-sign."
            }}])
    if validate_password(data.new_password):
        if validate_password(data.new_password) != True:
            return validate_password(data.new_password)

    password_hash = hashlib.sha256(
        (data.new_password + salt).encode('utf-8')).hexdigest()
    user.password = password_hash
    db.commit()
    return {'message': 'password has been changed successfully'}


def generate_unique_random_string(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    random_string = ''.join(random.choices(letters_and_digits, k=length))
    unique_string = f"{current_time}_{random_string}"
    return unique_string



@router.get('/generateToken')
def generateToken(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    id = verify_token_access(token).id
    user = db.query(User).filter(User.id == id).first()
    access_token =generate_unique_random_string()
    userDetail = db.query(UserDetail).filter(
        UserDetail.user_id == id).one_or_none()
    user_token = db.query(UserToken).filter(
        UserToken.userDetailId == userDetail.id).first()
    if user_token:
        user_token.token = access_token
    else:
        user_token = UserToken(userDetailId=userDetail.id, token=access_token)
        db.add(user_token)
    db.commit()
    return {'message': access_token}





