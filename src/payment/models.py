from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from database import Base


class PaymentMode(Base):
    __tablename__ = 'payment_modes'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(length=255), nullable=False)
    key = Column(String(length=255), nullable=False)
    token = Column(String(length=255), nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey('users.id'))
    payment_mode_id=Column(ForeignKey('payment_modes.id'))
    amount=Column(Integer,nullable=False)
    remarks=Column(String(length=255))

