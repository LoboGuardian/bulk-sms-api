from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
# from src.auth.models import ContactGroup
from contact.models import ContactGroup
# from database import Base
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(length=255), nullable=False)
    password = Column(String(length=255), nullable=False)
    email = Column(String(length=255), nullable=False)
    contact_group=relationship('ContactGroup',back_populates='user')
    user_detail = relationship(
        'UserDetail', back_populates='user', uselist=False)


class UserDetail(Base):
    __tablename__ = 'user_details'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_type = Column(String(length=255), nullable=False)
    sms_credit = Column(Float)
    rate = Column(Float)
    status = Column(Boolean, default=True)
    user = relationship('User', back_populates='user_detail')


