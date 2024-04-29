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
    subject:str
    description:str
    approved:bool


class DictionaryResponse(BaseModel):
    id:int
    wordd:str

