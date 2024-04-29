from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from auth.routers.login import oauth2_scheme, verify_token_access
from payment.schemas import PaymentData, TransactionCreate
from sqlalchemy.orm import Session
from database import get_db
from payment.models import Transaction
from auth.models import UserDetail

router = APIRouter(
    prefix='/transaction',
    tags=['transaction'],

)


@router.post('/save_transaction/{type}')
def createTransactionDetail(type:str, data: TransactionCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    verify_token_access(token)
    exist=db.query(Transaction).filter_by(transaction_code=data.transaction_code).one_or_none()
    paymentCode=0
    if type=='E-sewa':
        paymentCode=1
    elif type=='Khalti':
        paymentCode=3
    else:
        paymentCode=5
    if not exist:
        saveData = Transaction(user_id=data.user_id, payment_mode_id=paymentCode,
            amount=data.amount, remarks=data.remarks,transaction_code=data.transaction_code)
        # print(data.user_id)
        updateUserDetail=db.query(UserDetail).filter_by(
            user_id=data.user_id).one_or_none()
        updateUserDetail.sms_credit=(updateUserDetail.sms_credit + round(data.amount/updateUserDetail.rate))  
        db.add(saveData)
        db.commit()
        db.refresh(saveData)
        return {
            'message': 'Transaction saved'
        }   
    else:
        return {
            'message':'error occurred'
        }



