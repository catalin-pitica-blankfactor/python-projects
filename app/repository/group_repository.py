from sqlalchemy.orm import Session
import uuid
from app.model.group_model import Group


class GroupRepository:
    def get_group_by_id(self, db: Session, group_id: str):
        return db.query(Group).filter(Group.uuid == group_id).first()

    def get_all_groups(self, db: Session):
        return db.query(Group).all()

    def check_exist_group_name(self, db: Session, group_name):
        return db.query(Group).filter(Group.name == group_name).first()

    def create_group(self, db: Session, name: str):
        new_id = str(uuid.uuid4())
        db_group = Group(uuid=new_id, name=name)
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group

    def update_group(self, db: Session, group_id: str, group_name: str):
        db.query(Group).filter(Group.uuid == group_id).update({Group.name: group_name})
        db.commit()
        db_group_update = db.query(Group).filter(Group.uuid == group_id).first()
        return db_group_update

    def delete_group_by_id(self, db: Session, group_id: str):
        group = db.query(Group).filter(Group.uuid == group_id).first()
        db.delete(group)
        db.commit()
