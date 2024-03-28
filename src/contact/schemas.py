from pydantic import BaseModel
from typing import List, Optional
from auth.schemas import Users


class ContactGroupBase(BaseModel):
    title: str


class ContactGroupCreate(ContactGroupBase):
    pass


class ContactGroup(ContactGroupBase):
    id: int
    user_id: int
    user: Users

    class Config:
        from_attributes = True


class ContactBase(BaseModel):
    name: str
    phone: str
    whatsapp: Optional[str] = None
    email: str



class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: int
    group_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    contact_groups: List[ContactGroup] = []

    class Config:
        from_attributes = True



