from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

from database import Base
# from src.database import Base


class ContactGroup(Base):
    __tablename__ = 'contact_groups'
    user_id = Column(ForeignKey('users.id'))
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(length=255), nullable=False)
    user = relationship('User', back_populates='contact_group')
    contacts = relationship(
        'Contact', back_populates='contact_group')


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=255), nullable=False)
    phone = Column(String(length=20), nullable=False)
    whatsapp = Column(String(length=20))
    email = Column(String(length=255), nullable=False)
    group_id = Column(ForeignKey('contact_groups.id'))
    contact_group = relationship('ContactGroup', back_populates='contacts')


