from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from auth.routers.login import oauth2_scheme, verify_token_access
from payment.schemas import KhaltiPaymentData, PaymentData
from sqlalchemy.orm import Session
from database import get_db
import requests # type: ignore
import json


router = APIRouter(
    prefix='/payment',
    tags=['payment'],
    
)



@router.post('/payWithKhalti')
def payWithKhalti(data:KhaltiPaymentData, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    payload = json.dumps({
        "return_url": data.return_url,
        "website_url": data.website_url,
        "amount": data.amount,
        "purchase_order_id": data.purchase_order_id,
        "purchase_order_name": data.purchase_order_name,
    })
    headers = {
        'Authorization': 'key 95f8086631c24b4bbbbebc6d4aa37d14',
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return {'message':response.json()}