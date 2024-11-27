from sqlalchemy import Column, String, ForeignKey

from app.core.database import Base


class UserGroup(Base):
    __tablename__ = "user_group"

    user_uuid = Column(String, ForeignKey("user.uuid"), primary_key=True)
    group_uuid = Column(String, ForeignKey("group.uuid"), primary_key=True)
