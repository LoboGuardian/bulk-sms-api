from pydantic import BaseModel
from typing import List, Optional
from auth.schemas import Users
from pydantic import BaseModel
from typing import Annotated
from fastapi import FastAPI, Query

app = FastAPI()


class PaymentData(BaseModel):
    amount: str
    failure_url: str
    product_delivery_charge: str
    product_service_charge: str
    product_code: str
    signature: str
    signed_field_names: str
    success_url: str
    tax_amount: str
    total_amount: str
    transaction_uuid: str


class TransactionCreate(BaseModel):
    user_id: int
    payment_mode_id: str
    amount: int
    remarks: str
    transaction_code: str


class KhaltiPaymentData(BaseModel):
    amount: str
    total_amount: str
    return_url: str
    website_url: str
    purchase_order_id: str
    purchase_order_name: str


