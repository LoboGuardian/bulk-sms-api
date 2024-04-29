from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated
from contact.schemas import Contact, ContactGroup, ContactCreate, ContactGroupCreate
from database import get_db
from auth.routers.login import oauth2_scheme, verify_token_access
from sqlalchemy.orm import subqueryload
import math
# from contact.models import ContactGroup
import re
from database import SessionLocal

# from contact.schemas import ContactGroup, ContactCreate
from auth.models import User,UserDetail
import contact.schemas
import contact.models
import hashlib
router = APIRouter(
    prefix='/contacts',
    tags=['contacts'],
)



@router.get('/getDashboardData/{id}')
def totalContacts(id:int,token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    verify_token_access(token)
    # totalContacts=db.query(contact.models.Contact.contact_group).filter_by(contact.models.Contact.contact_group.user_id==1).count()
    totalContacts=db.query(contact.models.Contact).join(contact.models.ContactGroup).filter(contact.models.ContactGroup.user_id==id,contact.models.ContactGroup.title!='Unassigned').count()
    totalContactGroup=db.query(contact.models.ContactGroup).filter(contact.models.ContactGroup.user_id==id,contact.models.ContactGroup.title!='Unassigned').count()
    totalSmsCredit=db.query(UserDetail).filter_by(id=id).all()
   
    return {
        'totalContacts':totalContacts,
        'totalContactGroup':totalContactGroup,
        'totalSmsCredit': totalSmsCredit[0].sms_credit
    }

@router.get('/getContactByPageNumber/{pageNumber}')
def getContactByPage(pageNumber:int,token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    id=verify_token_access(token).id
    count=db.query(contact.models.Contact).join(contact.models.ContactGroup).filter(contact.models.ContactGroup.user_id==id).count()
    # unassignedGroup=db.query(contact.models.ContactGroup).filter(contact.models.ContactGroup.user_id==id).one_or_none()
    filtered=db.query(contact.models.Contact).join(contact.models.ContactGroup).filter(contact.models.ContactGroup.user_id==id).limit(5).offset((pageNumber-1)*5)
    totalCount=0
    if count==5:
        totalCount=1
    else:
        if count%5==0:
            totalCount=count/5
        else:
            totalCount=(count//5)+1
    return {'count':totalCount,'data':filtered.all()}



@router.get('/getAllContacts/', response_model=list[contact.schemas.Contact])
def getAllContacts( token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    id=verify_token_access(token).id
    allContacts=[]
    flattenedContacts=[]
    allContactGroup = db.query(contact.models.ContactGroup).filter(contact.models.ContactGroup.user_id==id).all()
    for i in allContactGroup:
        if len(i.contacts)!=0:
            allContacts.append(i.contacts)
    for i in range(len(allContacts)):
        for j in range(len(allContacts[i])):
            flattenedContacts.append(allContacts[i][j])
    return flattenedContacts

@router.get('/getAllContactGroup' ,response_model=list[contact.schemas.ContactGroup])
def getAllContactGroup( token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)
    data=db.query(contact.models.ContactGroup).all()
    return data

@router.get('/getContactbyId/{id}', response_model=contact.schemas.Contact)
def getContactById(id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)
    data = db.query(contact.models.Contact).filter(
        contact.models.Contact.id == id).first()

    return data


@router.get('/contact_groups/{user_id}', response_model=list[contact.schemas.ContactGroup])
def getContactGroup(user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)
    data = db.query(contact.models.ContactGroup).filter(
        contact.models.ContactGroup.user_id == user_id,contact.models.ContactGroup.title!='Unassigned').all()
    return data



@router.get('/{groupId}/{pageNumber}',response_model=contact.schemas.ContactPaginated)
def getContacts(groupId: int,pageNumber:int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)
    count= db.query(contact.models.Contact).filter(
        contact.models.Contact.group_id == groupId).count()
    data = db.query(contact.models.Contact).filter(
        contact.models.Contact.group_id == groupId).limit(5).offset((pageNumber-1)*5)
    totalCount=0
    if count==5:
        totalCount=1
    else:
        if count%5==0:
            totalCount=count/5
        else:
            totalCount=(count//5)+1
    return {'count':totalCount,'data':data.all()}


@router.post('/{id}')
def createContacts( contactDetail: contact.schemas.ContactCreate,id:int,contactGroupId:int|None=None, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)
    if not contactDetail.group_id:
        UnassignedGroup=db.query(contact.models.ContactGroup).filter(contact.models.ContactGroup.user_id==id,contact.models.ContactGroup.title=='unassigned').all()
        groupId=UnassignedGroup[0].id
    else:
        groupId=contactDetail.group_id
    data = contact.models.Contact(name=contactDetail.name, phone=contactDetail.phone,
                                  whatsapp=contactDetail.whatsapp, email=contactDetail.email)
    data.group_id=groupId
    db.add(data)
    db.commit()
    db.refresh(data)
    return {
        'message': 'Contact created'
    }


@router.post('/contactGroupId/{group_id}')
def createContact(contactDetail: contact.schemas.ContactCreate, group_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # new_contact_create = contact.models.Contact(name=contactDetail.name,phone=contactDetail.phone,whatsapp=contactDetail.whatsapp,email=contactDetail.email, group_id=group_id)
    verify_token_access(token)
    data = db.query(contact.models.Contact).filter(
        contact.models.Contact.id == contactDetail.id).first()
    data.group_id = group_id
    # db.add(new_contact_create)
    db.commit()
    db.refresh(data)
    return {
        'message': 'Contact created'
    }



@router.put('/{contact_id}')
def edit_contact(contact_id: int, contact_edit_data: contact.schemas.ContactEdit, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token_access(token)
    data = db.query(contact.models.Contact).filter(
        contact.models.Contact.id == contact_id).first()
    if data:
        # Update the contact fields if they are provided in the contact_edit_data
        if contact_edit_data.name:
            data.name = contact_edit_data.name
        if contact_edit_data.phone:
            data.phone = contact_edit_data.phone
        if contact_edit_data.whatsapp is not None:
            data.whatsapp = contact_edit_data.whatsapp
        if contact_edit_data.email:
            data.email = contact_edit_data.email
        if contact_edit_data.group_id:
            data.group_id=contact_edit_data.group_id
        db.commit()
        db.refresh(data)
        return data


@router.delete('/{contact_id}')
def delete_contact(contact_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token_access(token)
    data = db.query(contact.models.Contact).filter_by(
        id=contact_id).one_or_none()
    db.delete(data)
    db.commit()
    return {'message': 'Contact Deleted'}



@router.post('/contact_groups/{user_id}')
def createGroup(contactGroup: contact.schemas.ContactGroupCreate, user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token_access(token)
    new_contact_group = contact.models.ContactGroup(
        title=contactGroup.title, user_id=user_id)
    db.add(new_contact_group)
    db.commit()
    db.refresh(new_contact_group)
    data = db.query(contact.models.ContactGroup).filter(
        contact.models.ContactGroup.user_id == 1).first()
    return {'message': 'Contact created'}



@router.put('/contact_groups/{id}', response_model=contact.schemas.ContactGroup)
def update_contact_groups(contactGroup: contact.schemas.ContactGroupCreate, id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)
    data = db.query(contact.models.ContactGroup).filter_by(
        id=id).one_or_none()
    # print(contactGroup.title)
    data.title = contactGroup.title
    db.commit()
    return data


@router.delete('/unassignFromContactGroup/{contact_group_id}/{contact_id}')
def removeFromGroup(contact_group_id:int,contact_id:int,db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    id=verify_token_access(token).id
    data=db.query(contact.models.Contact).filter(contact.models.Contact.id==contact_id,contact.models.Contact.group_id==contact_group_id).one_or_none()
    unassignedGroup=db.query(contact.models.ContactGroup).filter(contact.models.ContactGroup.user_id==id,contact.models.ContactGroup.title=='Unassigned').one_or_none()
    data.group_id=unassignedGroup.id
    db.commit()
    return {'message':"Contact removed from the group"}



@router.delete('/contact_groups/{contact_group_id}')
def delete_contact_group(contact_group_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    userid=verify_token_access(token).id
    data = db.query(contact.models.ContactGroup).filter_by(
        id=contact_group_id).one_or_none()
    unassignedGroup=db.query(contact.models.ContactGroup).filter(contact.models.ContactGroup.user_id==userid,contact.models.ContactGroup.title=='Unassigned').one_or_none()

    for cont in data.contacts:
        cont.group_id=unassignedGroup.id
    
    db.commit()
    db.delete(data)
    db.commit()
    return {'message': "Contact group removed"}


@router.get('/searchContact')
def searchContact(text:str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    id=verify_token_access(token).id
    # clostData=db.query(contact.models.Contact).filter(contact.models.Contact)
    # parent=db.get(contact.models.Contact)
    data=db.query(contact.models.Contact).join(contact.models.ContactGroup).filter(contact.models.Contact.name.contains(text),contact.models.ContactGroup.user_id==id).all()

    return data



