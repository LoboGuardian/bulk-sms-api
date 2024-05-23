from datetime import datetime
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from auth.routers.login import oauth2_scheme, verify_token_access
from sms.schemas import SendBulkSms, SmsPost, DictionaryResponse
from sms.models import BatchContacts, SmsBatch, MessageQueue, Dictionary
from contact.models import Contact
from sqlalchemy.orm import Session
from database import get_db
import requests  # type: ignore
import json
from auth.models import UserDetail, UserToken

import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("../../../")/".env"
load_dotenv(dotenv_path=env_path)


USER_NAME = os.getenv("USER_NAME")
BULKSMSPASSWORD = os.getenv('BULKSMSPASSWORD')
ORGANISATIONCODE = os.getenv('ORGANISATIONCODE')
BULKSMSURL = os.getenv('BULKSMSURL')
SEND_MULTIPLE_SMS_URL = os.getenv('SEND_MULTIPLE_SMS_URL')


router = APIRouter(
    prefix='/sms',
    tags=['sms'],
)


@router.post('/sms_batch')
async def postSmsData(data: SmsPost, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)
    userDetail = getUser(data.id, db)
    userCredits = userDetail.sms_credit
    # checking if the user has sms credit or not
    if userDetail.user_type != 'Admin':
        if userDetail.status == False:
            raise HTTPException(
                status_code=403, detail="Account has been blocked. Please contact adminstrator for further adminstration")
        if not hasCredit(data.id, db):
            raise HTTPException(
                status_code=402, detail="User needs to add credits inorder to send message.")

    contactIds = []
    recipientContacts = []
    schedule_time = datetime.fromisoformat(
        data.schedule_time) if data.schedule_time != None and data.schedule_time != "" else None

    if data.approved == False:
        addData = SmsBatch(user_id=data.id, message_body=data.description,
                           sms_rate=userDetail.rate, schedule_type=data.schedule_type, approved=data.approved, schedule_time=schedule_time)

        db.add(addData)
        db.flush()
        db.refresh(addData)
        addData.batch_number = f'batchId_{addData.id}'
        db.commit()
        return {'message': "Your message has been temporarily halted for verification by our moderators. We'll review it shortly. Thank you for your understanding.", 'credits': userDetail.sms_credit}

    # inserting all the numbers into an array

    addData = SmsBatch(user_id=data.id, message_body=data.description,
                       sms_credit_reduction=data.smsCredit,
                       sms_rate=userDetail.rate, schedule_type=data.schedule_type, approved=data.approved, schedule_time=schedule_time)

    db.add(addData)
    db.flush()
    db.refresh(addData)
    addData.batch_number = f'batchId_{addData.id}'

    for i in data.group_id:
        contactNumber = db.query(Contact).filter(
            Contact.group_id == i).all()
        for j in range(len(contactNumber)):
            contactIds.append(contactNumber[j].phone)
    for i in range(len(data.reciepents)):
        contactIds.append(data.reciepents[i])
        recipientContacts.append(data.reciepents[i])
    if len(contactIds) == 0:
        raise HTTPException(status_code=400, detail="Contact is empty.")

    if data.schedule_type == 'Now':
        for contactNumber in contactIds:
            if await process_request(contactNumber, data, addData, db):
                userCredits -= data.smsCredit
                if userCredits == -1:
                    userDetail.sms_credit = userCredits
                    db.commit()
                    raise HTTPException(
                        status_code=402, detail="User needs to add credits inorder to send message.")
        userDetail.sms_credit = userCredits
        db.commit()
        return {'message': 'Message has been sent successfully', 'credits': userDetail.sms_credit}
    else:
        objects = []
        for i in contactIds:
            objects.append(BatchContacts(contactNumber=i, batch_id=addData.id))
        db.bulk_save_objects(objects)
        db.commit()
        return {'message': 'Message has been scheduled for future', 'credits': userDetail.sms_credit}


@router.get('/getSwearWords', response_model=list[DictionaryResponse])
def getSwearWords(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)
    swearWords = db.query(Dictionary).all()
    return swearWords


def hasCredit(id, db):
    userDetail = db.query(UserDetail).filter(UserDetail.user_id == id).first()
    if userDetail.sms_credit == 0.00:
        return False
    return True


def getUser(id, db):
    userDetail = db.query(UserDetail).filter(UserDetail.user_id == id).first()
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


async def process_request(contactNumber, data, addData, db):
    try:
        message = data.description
    except:
        message = data.message_body
    if await createRequest(contactNumber, message):
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


async def createRequest(receiver, description):
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
    finalResponse = response.json()
    if finalResponse['responseCode'] == 100:
        return True
    return False


def get_current_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%m/%d/%Y %H:%M")
    return formatted_time


@router.post('/sendSms')
async def sendSms(data: SendBulkSms, db: Session = Depends(get_db)):
    userDetail = db.query(UserToken).filter(
        UserToken.token == data.token).one_or_none()
    if not userDetail:
        return {"message": 'Provided token is not correct'}
    userDetail = getUser(userDetail.userDetailId, db)
    # checking if the user has sms credit or not
    if userDetail.status == False:
        raise HTTPException(
            status_code=403, detail="Account has been blocked. Please contact adminstrator for further adminstration.")

    if not hasCredit(userDetail.user_id, db):
        raise HTTPException(
            status_code=402, detail="User needs to add credits inorder to send message.")
    # userDetail.sms_credit=userCredits
    smsDetails = []
    for i in data.list:
        appendableData = {
            'Message': data.message,
            'ReceiverNo': i
        }
        smsDetails.append(appendableData)
    addData = SmsBatch(user_id=userDetail.user_id, message_body=data.message,
                       sms_rate=userDetail.rate, schedule_type='Now', approved=True)
    db.add(addData)
    db.flush()
    db.refresh(addData)
    addData.batch_number = f'batchId_{addData.id}'
    db.commit()
    BulkSmsData = {
        "IsClientLogin": "N",
        "SmsDetails": smsDetails,
        "BatchId": f'batchId_{addData.id}',
        "Date": str(get_current_time())
    }
    response = await sendBulkSms(BulkSmsData)

    if response:
        userCredits = userDetail.sms_credit - len(smsDetails)
        userDetail.sms_credit = userCredits
        db.commit()

    return {'message': 'Sent successfully'} if response else {'message': 'Internal server error'}


async def sendBulkSms(payload):
    headers = {
        'OrganisationCode': ORGANISATIONCODE,
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", SEND_MULTIPLE_SMS_URL, auth=(
        USER_NAME, BULKSMSPASSWORD), headers=headers, data=json.dumps(payload))
    finalResponse = response.json()
    if finalResponse['responseCode'] == 100:
        return True
    return False


@router.get('/getToken')
def getToken(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    id = verify_token_access(token).id
    tokenData = db.query(UserToken).filter(
        UserToken.userDetailId == id).one_or_none()
    return {'data': tokenData.token} if tokenData else {'data': ''}


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
