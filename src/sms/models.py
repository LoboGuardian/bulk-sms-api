from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship

# from src.database import Base
from database import Base



class SmsBatch(Base):
    __tablename__ = 'sms_batch'
    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String(255))
    user_id = Column(ForeignKey('users.id'))
    message_body = Column(Text, nullable=False)
    sms_rate = Column(Float)
    schedule_type = Column(String(255))
    schedule_time = Column(DateTime)
    sms_credit_reduction=Column(Integer)

    approved = Column(Boolean)
    queues = relationship("MessageQueue", back_populates='smsbatch')
    batchContact=relationship('BatchContacts',back_populates='smsbatch')


class MessageQueue(Base):
    __tablename__ = 'message_queue'
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(ForeignKey('sms_batch.id'))
    sendTo = Column(String(13))
    provider = Column(String(10))
    status = Column(Boolean)
    smsbatch = relationship('SmsBatch', back_populates='queues')


class Dictionary(Base):
    __tablename__='dictionary'
    id = Column(Integer, primary_key=True, index=True)
    wordd=Column(String(255))



class BatchContacts(Base):
    __tablename__='batch_contacts'
    id = Column(Integer, primary_key=True, index=True)
    contactNumber=Column(String(length=20), nullable=False)
    batch_id = Column(ForeignKey('sms_batch.id'))
    smsbatch = relationship('SmsBatch', back_populates='batchContact')





