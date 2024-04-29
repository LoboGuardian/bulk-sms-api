from fastapi import APIRouter, Depends, HTTPException, Query
# from src.auth.schemas import Users
from auth.schemas import Users,UserDetailResponse
from auth.models import User,UserDetail
from fastapi import FastAPI, Form
# from auth.utils import Authenticate
from pydantic import BaseModel, EmailStr, Field, validator
from contact.models import ContactGroup
# from utils import Authenticate
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from utils import has_only_english_characters
from typing import Annotated
from database import get_db
import re
from database import SessionLocal
import hashlib
router = APIRouter(
    prefix='/users',
    tags=['users'],
)


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
                    "password"
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
                            password=password_hash, email=email)
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
                db.commit()
                # Refresh the user instance to access its generated id
                db.refresh(new_user)
                savableData=UserDetail(user_id=new_user.id,user_type='Client',sms_credit=0,rate=1,status=True)
                db.add(savableData)
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



@router.get('/getUserDetail/{id}',tags=['users'],response_model=UserDetailResponse)
async def getUserDetail(id:int,db: Session = Depends(get_db)):
    data=db.query(UserDetail).filter(UserDetail.user_id==id).one_or_none()
    return data



