from pydantic import BaseModel
from typing import List, Optional
from auth.schemas import Users
from pydantic import BaseModel, EmailStr, validator
from typing import Annotated
from fastapi import FastAPI, Query
from utils import has_only_english_characters


app = FastAPI()


@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


def validate_username(v):
    if not has_only_english_characters(v):
        raise ValueError("Contact name must contain only letters")
    return v


class ContactGroupBase(BaseModel):
    title: str
    _validate_username = validator(
        'title', allow_reuse=True)(validate_username)


class ContactGroupCreate(ContactGroupBase):
    pass


class ContactGroup(ContactGroupBase):
    id: int
    user_id: int
    contacts: List['Contact'] = []
    # user: Optional[Users] = None

    class Config:
        from_attributes = True


def has_white_spaces(text):
    return any(char.isspace() for char in text)


class ContactBase(BaseModel):
    name: str
    phone: Annotated[str, Query(min_length=10, max_length=15)]
    whatsapp: Annotated[str, Query(min_length=10, max_length=15)]
    email: EmailStr
    _validate_username = validator('name', allow_reuse=True)(validate_username)

# class ContactBase(BaseModel):
#     name: str
#     # phone: int
#     phone: int
#     whatsapp: Optional[str] = None
#     email: EmailStr


class ContactEdit(ContactBase):
    name: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None


class ContactCreate(ContactBase):
    id: Optional[int] = None
    pass


class Contact(ContactBase):
    id: int
    group_id: Optional[int] = None
    # contact_group: ContactGroup = None

    class Config:
        from_attributes = True

class ContactPaginated(BaseModel):
    count: int
    data: List[Contact]

class ContactResponse(BaseModel):
    count:int
    data:list[Contact]=[]
    class Config:
        from_attributes=True


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    contact_groups: List[ContactGroup] = []

    class Config:
        from_attributes = True
