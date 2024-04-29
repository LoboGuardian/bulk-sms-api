from pydantic import BaseModel
import datetime

from sqlalchemy import DateTime


class Users(BaseModel):
    user_name: str
    email:str
    password: str
    class Config:
        from_attributes = True


class UserDetails(BaseModel):
    user_type: str
    sms_credit: float
    rate: float
    status: bool

    class Config:
        from_attributes = True

class UserDetailResponse(UserDetails):
    id:int
    user_id:int

    class Config:
        from_attributes = True

class UsersResponse(BaseModel):
    id:int
    user_name:str
    created_at:datetime.datetime
    user_detail:UserDetails
    # sms_credit:int
    # rate:int

    class Config:
        from_attributes = True





