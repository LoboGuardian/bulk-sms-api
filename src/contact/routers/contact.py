from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated
from contact.schemas import Contact, ContactGroup,ContactCreate,ContactGroupCreate
from database import get_db
import re
from database import SessionLocal
import hashlib
router = APIRouter(
    prefix='/contacts',
    tags=['contacts'],
)


@router.get('/here')
def getData(db: Session = Depends(get_db)):
    new_contact_group = ContactGroupCreate(title="Family")

    contact1 = ContactCreate(name="John Doe", phone="123456789", email="john@example.com", group=new_contact_group)
    contact2 = ContactCreate(name="Jane Smith", phone="987654321", email="jane@example.com", group=new_contact_group)
    # Add the contact group and contacts to the session
    db.add(new_contact_group)
    db.add(contact1)
    db.add(contact2)
    # Commit the changes to the database
    db.commit()
    return {'sampple': 'data'}

