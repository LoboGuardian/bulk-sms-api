from pydantic import BaseModel
from typing import List, Optional
from auth.schemas import Users
from pydantic import BaseModel
from typing import Annotated
from fastapi import FastAPI, Query

api=FastAPI()

class SmsPost(BaseModel):
    id:int
    group_id:Optional[list[int]]=None
    reciepents:Optional[list[int]]=None
    description:str
    smsCredit:int
    schedule_type:Optional[str]=None
    schedule_time:Optional[str]=None
    approved:bool


class DictionaryResponse(BaseModel):
    id:int
    wordd:str


class SendBulkSms(BaseModel):
    message:str
    token:str
    list:list[int]
