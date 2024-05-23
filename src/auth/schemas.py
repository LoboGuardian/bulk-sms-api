from pydantic import BaseModel
import datetime

from sqlalchemy import DateTime


class Users(BaseModel):
    user_name: str
    email:str
    phone_number:str
    company_name:str
    company_address:str
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

class ChangePassword(BaseModel):
    current_password:str
    new_password:str
    confirm_new_password:str
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

class GetAllUsersResponse(BaseModel):
    count: int
    data: list[UsersResponse]

class UpdateUser(BaseModel):
    user_name:str
    email:str
    company_name:str
    company_address:str
    phone_number:str


class ForgetPasswordRequest(BaseModel):
    email: str

class ResetForegetPassword(BaseModel):
    secret_token: str
    new_password: str
    confirm_password: str

class SuccessMessage(BaseModel):
    success: bool
    status_code: int
    message: str


class SaveSettingData(BaseModel):
    esewa_token:str
    khalti_token:str
    default_rate:str
