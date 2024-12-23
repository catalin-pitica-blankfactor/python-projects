from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Group(Base):
    __tablename__ = "group"

    uuid = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    user = relationship("User", secondary="user_group", back_populates="group", overlaps="group")
