from sqlalchemy.orm import Session, joinedload
from app.model.user_model import User
from app.model.group_model import Group
import uuid
import json


class UserRepository:
    def get_user_by_id(self, db: Session, user_id: str):
        return db.query(User).filter(User.uuid == user_id).first()

    def get_user_by_name(self, db: Session, user_name: str):
        return db.query(User).filter(User.name == user_name).first()

    def get_all_users(self, db: Session):
        return db.query(User).options(joinedload(User.group)).all()

    def create_user(self, db: Session, user_name: str, user_group: str):
        group_for_user = db.query(Group).filter(Group.uuid == user_group).first()
        new_id = str(uuid.uuid4())
        db_user = User(uuid=new_id, name=user_name)
        db_user.group.append(group_for_user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update_user_url(self, db: Session, user_id: str, updated_content: json):
        user = db.query(User).filter(User.uuid == user_id).first()
        user.urls = updated_content
        db.commit()
        db.refresh(user)

    def update_user(self, db: Session, user_id: str, user_name: str):
        db.query(User).filter(User.uuid == user_id).update({User.name: user_name})
        db.commit()
        user_updated = db.query(User).filter(User.uuid == user_id).first()
        return user_updated

    def delete_user(self, db: Session, user_id: str):
        user = db.query(User).filter(User.uuid == user_id).first()
        db.delete(user)
        db.commit()
