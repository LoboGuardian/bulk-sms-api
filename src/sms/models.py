from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

# from src.database import Base
from database import Base


class SmsBatch(Base):
    id=Column(Integer,primary_key=True,index=True)
    batch_number=Column(Integer,nullable=False)