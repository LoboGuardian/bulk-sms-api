from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from starlette.responses import JSONResponse

from starlette.background import BackgroundTasks
from pydantic import BaseModel
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from auth.models import User
from auth.schemas import ForgetPasswordRequest, ResetForegetPassword, SuccessMessage
from config import settings
from database import get_db
from auth.routers.users import validate_password
from pathlib import Path
import hashlib


base_dir = Path(__file__).resolve().parent.parent

env_path = os.path.join(base_dir, '.env')

load_dotenv(dotenv_path=env_path)

ALGORITHM = os.getenv('ALGORITHM')
SECRET_KEY = os.getenv('SECRET_KEY')
Mail_Server = os.getenv('MAIL_SERVER')

router = APIRouter(
    prefix='/users',
    tags=['users'],
)


conf = ConnectionConfig(
    MAIL_USERNAME="piyush.ratna.64@gmail.com",
    MAIL_PASSWORD="geox xzyb ouiu pkvt",
    MAIL_FROM="piyush.ratna.64@gmail.com",
    MAIL_PORT=465,
    MAIL_SERVER=Mail_Server,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).resolve().parent.parent / 'templates',
)


def create_reset_password_token(email: str):
    data = {"sub": email, "exp": datetime.now() + timedelta(minutes=10)}
    token = jwt.encode(data, SECRET_KEY, ALGORITHM)
    return token

def decode_reset_password_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY,
                   algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None 


def get_user(email, db: Session = Depends(get_db)):
    user=db.query(User).filter(User.email==email).one_or_none()
    return user


@router.post("/forget-password")
async def forget_password(
    background_tasks: BackgroundTasks,
    fpr: ForgetPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        user = get_user(email=fpr.email, db=db)
        if user is None:
           raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                  detail="Invalid Email address")
        secret_token = create_reset_password_token(email=fpr.email)
        forget_url_link = f"{secret_token}"
        email_body = {"company_name": 'Grumpy',
                      "link_expiry_min": '60',
                      "reset_link": forget_url_link}

        message = MessageSchema(
            subject="Password Reset Instructions",
            recipients=[fpr.email],
            body=f"<p>Company name : Bulk sms</p><p>Link expiry: 60 min</p><p>Reset Link http://localhost:5173/auth/resetPassword?token={str(forget_url_link)}</p>",
            subtype=MessageType.html
        )
        template_name = "password_reset.html"
        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, message)
        # await fm.send_message(message)
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"message": "Email has been sent", "success": True,
                                     "status_code": status.HTTP_200_OK})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something Unexpected, Server Error")



@router.post("/reset-password", response_model=SuccessMessage)
async def reset_password(
    rfp: ResetForegetPassword,
    db: Session = Depends(get_db)
):
    try:
        info = decode_reset_password_token(token=rfp.secret_token)
        if info is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   detail="Invalid Password Reset Payload or Reset Link Expired")
        if rfp.new_password != rfp.confirm_password:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   detail="New password and confirm password are not same.")
        salt = "Your Salt"
        if validate_password(rfp.new_password):
            if validate_password(rfp.new_password) != True:
                return validate_password(rfp.new_password)
            password_hash = hashlib.sha256(
                (rfp.new_password + salt).encode('utf-8')).hexdigest()
    
        # hashed_password = pwd_context.hash(rfp.new_password) 
            user = get_user(email=info, db=db)
            user.password = password_hash
            db.add(user)
            db.commit()
        return {'success': True, 'status_code': status.HTTP_200_OK,
                 'message': 'Password Reset Successfull!'}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Some thing unexpected happened!")

# @app.post("/reset-password", response_model=SuccessMessage)
# async def reset_password(
#     rfp: ResetForegetPassword,
#     db: Session = Depends(get_db_session)
# ):
#     try:
#         info = decode_reset_password_token(token=rfp.secret_token)
#         if info is None:
#             raise HttpException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                    detail="Invalid Password Reset Payload or Reset Link Expired")
#         if rfp.new_password != rfp.confirm_password:
#             raise HttpException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                    detail="New password and confirm password are not same.")

#         hashed_password = pwd_context.hash(rfp.new_password)
#         user = get_user(email_ads=info, db=db)
#         user.password = hashed_password
#         db.add(user)
#         db.commit()
#         return {'success': True, 'status_code': status.HTTP_200_OK,
#                  'message': 'Password Rest Successfull!'}
#     except Exception as e:
#         raise HttpException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#               detail="Some thing unexpected happened!")
