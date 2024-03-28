from pydantic import BaseModel


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






