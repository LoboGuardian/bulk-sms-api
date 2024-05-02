from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
import datetime
# from src.auth.models import ContactGroup
# from contact.models import ContactGroup
from database import Base
# from src.database import Base

from sqlalchemy_easy_softdelete.mixin import generate_soft_delete_mixin_class
from sqlalchemy_easy_softdelete.hook import IgnoredTable



class SoftDeleteMixin(generate_soft_delete_mixin_class(
    # This table will be ignored by the hook
    # even if the table has the soft-delete column
    ignored_tables=[IgnoredTable(table_schema="public", name="cars"),]
)):
    # type hint for autocomplete IDE support
    deleted_at: datetime.datetime

# Apply the mixin to your Models
class User(Base,SoftDeleteMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(length=255), nullable=False)
    password = Column(String(length=255), nullable=False)
    email = Column(String(length=255), nullable=False)
    created_at = Column(DateTime,
                        default=datetime.datetime.now(datetime.UTC))
    contact_group = relationship('ContactGroup', back_populates='user')
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



