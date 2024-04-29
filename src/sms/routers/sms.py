import re
from fastapi import APIRouter, Depends, HTTPException, Query
from auth.routers.login import oauth2_scheme, verify_token_access
from sms.schemas import SmsPost,DictionaryResponse
from sms.models import SmsBatch, MessageQueue,Dictionary
from contact.models import Contact
from sqlalchemy.orm import Session
from database import get_db
import requests  # type: ignore
import json
from auth.models import UserDetail

import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("../../../")/".env"
load_dotenv(dotenv_path=env_path)


USER_NAME = os.getenv("USER_NAME")
BULKSMSPASSWORD = os.getenv('BULKSMSPASSWORD')
ORGANISATIONCODE = os.getenv('ORGANISATIONCODE')
BULKSMSURL = os.getenv('BULKSMSURL')


router = APIRouter(
    prefix='/sms',
    tags=['sms'],
)



@router.post('/sms_batch')
def postSmsData(data: SmsPost, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)

    userDetail=getUser(data.id,db)
    userCredits=userDetail.sms_credit
    #checking if the user has sms credit or not
    if userDetail.status==False:
        raise HTTPException(status_code=403, detail="User needs to be active.")

    if not hasCredit(data.id,db):
        raise HTTPException(status_code=402, detail="User needs to add credits inorder to send message.")

    contactIds = []

    if data.approved==False:
        addData = SmsBatch(user_id=data.id, message_body=data.description,
                       sms_rate=userDetail.rate, schedule_type='Now', approved=data.approved)
    
        #nooob
        db.add(addData)
        db.flush()
        db.refresh(addData)
        addData.batch_number = f'batchId_{addData.id}'
        db.commit()
        return {'message': "Your message has been temporarily halted for verification by our moderators. We'll review it shortly. Thank you for your understanding.",'credits':userDetail.sms_credit}

    # inserting all the numbers into an array
    for i in range(len(data.group_id)):
        contactNumber = db.query(Contact).filter(Contact.group_id == i).all()
        for j in range(len(contactNumber)):
            contactIds.append(contactNumber[j].phone)
    for i in range(len(data.reciepents)):
        contactIds.append(data.reciepents[i])
    if len(contactIds)==0:
        raise HTTPException(status_code=400, detail="Contact is empty.")


    addData = SmsBatch(user_id=data.id, message_body=data.description,
                       sms_rate=userDetail.rate, schedule_type='Now', approved=data.approved)
    
    #nooob
    db.add(addData)
    db.flush()
    db.refresh(addData)
    addData.batch_number = f'batchId_{addData.id}'

    for contactNumber in contactIds:
         if process_request(contactNumber, data, addData, db):
            userCredits-=1
            if userCredits==-1:
                userDetail.sms_credit=userCredits
                db.commit()
                raise HTTPException(status_code=402, detail="User needs to add credits inorder to send message.")
    userDetail.sms_credit=userCredits
    db.commit()
    return {'message': 'Message has been sent successfully','credits':userDetail.sms_credit}

@router.get('/getSwearWords',response_model=list[DictionaryResponse])
def getSwearWords(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)
    swearWords=db.query(Dictionary).all()
    return swearWords


def hasCredit(id,db):
    userDetail=db.query(UserDetail).filter(UserDetail.user_id==id).first()
    if userDetail.sms_credit==0.00:
        return False
    return True

def getUser(id,db):
    userDetail=db.query(UserDetail).filter(UserDetail.user_id==id).first()
    return userDetail


def check_phone_number(phone_number):
    ntc_pattern = re.compile(r'^9[78][4-6]\d{7}$')
    ncell_pattern = re.compile(r'^98[0-3]\d{7}$')
    smart_pattern = re.compile(r'^96[12]\d{7}$')
    smart_pattern2 = re.compile(r'^988\d{7}$')

    if ntc_pattern.match(phone_number):
        return "NTC"
    elif ncell_pattern.match(phone_number):
        return "Ncell"
    elif smart_pattern.match(phone_number) or smart_pattern2.match(phone_number):
        return "Smart"
    else:
        return "Invalid"


def process_request(contactNumber, data, addData, db):
    if createRequest(contactNumber, data.description):
        status = True
    else:
        status = False
    
    messageQues = MessageQueue(
        batch_id=addData.id,
        sendTo=str(contactNumber),
        provider=check_phone_number(str(contactNumber)),
        status=status
    )
    db.add(messageQues)
    db.commit()
    return status



def createRequest(receiver,description):
    payload = {
        "IsClientLogin": "N",
        "ReceiverNo": receiver,
        "Message": description
    }
    headers = {
        'OrganisationCode': ORGANISATIONCODE,
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", BULKSMSURL, auth=(
        USER_NAME, BULKSMSPASSWORD), headers=headers, data=json.dumps(payload))
    finalResponse=response.json()
    if finalResponse['responseCode']==100:
        return True
    return False






# @router.post('/payWithKhalti')
# def payWithKhalti(data:KhaltiPaymentData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     url = "https://a.khalti.com/api/v2/epayment/initiate/" #env for later use
#     payload = json.dumps({
#         "return_url": data.return_url,
#         "website_url": data.website_url,
#         "amount": data.amount,
#         "purchase_order_id": data.purchase_order_id,
#         "purchase_order_name": data.purchase_order_name,
#     })
#     headers = {
#         'Authorization': 'key 95f8086631c24b4bbbbebc6d4aa37d14',
#         'Content-Type': 'application/json',
#     }
#     response = requests.request("POST", url, headers=headers, data=payload)
#     return {'message':response.json()}





