import json
import time
from fastapi import APIRouter, Depends
from celery import shared_task, Celery
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from celery.schedules import crontab
from sqlalchemy.orm import Session
from sms.models import SmsBatch
from auth.models import UserDetail
from sms.models import BatchContacts
from database import get_db, SessionLocal
from sms.routers.sms import process_request
from fastapi.encoders import jsonable_encoder
from asgiref.sync import async_to_sync
# from config import settings
import asyncio

load_dotenv()


router = APIRouter(
    prefix='/tasks',
    tags=['tasks'],
)
# celery = Celery('tasks',backend='rpc://',
#                 broker='')

celery = Celery('tasks', backend='rpc://',
                broker=os.environ.get("CELERY_BROKER_URL"))

celery.conf.timezone = 'UTC'

# @celery.task
# def add(x, y):
#     print(x,y)
#     return x + y


@celery.task
def databaseResults():
    result = asyncio.run(montiorDatabase())
    json_result = json.dumps(result)
    return json_result


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5.0, databaseResults.s(), name='add every 30')


async def montiorDatabase():
    # batch=db.query(SmsBatch).all()
    db = SessionLocal()
    contacts = []
    current_time = datetime.now()

    batches = db.query(SmsBatch).join(BatchContacts).filter(SmsBatch.schedule_type == 'Later',
                                                            SmsBatch.schedule_time < current_time).all()
    userId = []

    userSmsCredReduce = {}

    if len(batches) > 0:
        for batch in batches:
            userId.append(batch.user_id)
            for contact in batch.batchContact:
                if await process_request(contact.contactNumber, batch, batch, db):
                    userSmsCredReduce[userId[len(
                        userId)-1]] = (userId[len(userId)-1]-userId[len(userId)-1])+1
            batch.schedule_type = 'Now'
            db.commit()
    for id in userId:
        userData = db.query(UserDetail).filter(UserDetail.user_id == id).all()
        userData[0].sms_credit = userData[0].sms_credit-userSmsCredReduce[id]
    db.commit()
    return {}







