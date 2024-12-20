from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "user"

    uuid = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    urls = Column(JSON, index=True, nullable=True)
    group = relationship("Group", secondary="user_group", back_populates="user", overlaps="user")
