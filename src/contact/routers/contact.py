from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated
from contact.schemas import Contact, ContactGroup, ContactCreate, ContactGroupCreate
from database import get_db
# from contact.models import ContactGroup
import re
from database import SessionLocal

# from contact.schemas import ContactGroup, ContactCreate
from auth.models import User
import contact.schemas
import contact.models
import hashlib
router = APIRouter(
    prefix='/contacts',
    tags=['contacts'],
)


@router.post('/create_group/{user_id}', response_model=contact.schemas.ContactGroup)
def createGroup(contactGroup: contact.schemas.ContactGroupCreate, user_id: int, db: Session = Depends(get_db)):
    new_contact_group = contact.models.ContactGroup(
        **contactGroup, user_id=user_id)
    db.add(new_contact_group)
    db.commit()
    db.refresh(new_contact_group)
    data = db.query(contact.models).filter(
        contact.models.ContactGroup.user_id == 1).first()
    return data


@router.post('/create_contact/{group_id}')
def createContact(contactDetail: contact.schemas.ContactCreate, group_id: int, db: Session = Depends(get_db)):
    # new_contact_create = contact.models.Contact(name=contactDetail.name,phone=contactDetail.phone,whatsapp=contactDetail.whatsapp,email=contactDetail.email, group_id=group_id)
    new_contact_create = contact.models.Contact(
        **contactDetail.dict(), group_id=group_id)
    db.add(new_contact_create)
    db.commit()
    db.refresh(new_contact_create)
    return {
        'message': 'Contact created'
    }
    # pass
