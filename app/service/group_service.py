from enum import Enum
from typing import Any
from sqlalchemy.orm import Session
from app.repository.group_repository import GroupRepository


class GroupType(str, Enum):
    REGULAR = "regular"
    ADMIN = "admin"


class GroupService:
    def __init__(self):
        self.group_repository = GroupRepository()

    def add_new_group(self, db: Session, name: str) -> Any:
        if name not in {group.value for group in GroupType}:
            raise ValueError(
                f"Group name must be {GroupType.REGULAR.value} or {GroupType.ADMIN.value}"
            )
        return self.group_repository.create_group(db, name)

    def check_existing_group_name(self, db: Session, group_name: str):
        if self.group_repository.check_exist_group_name(db, group_name):
            raise KeyError(f"Group with the name: {group_name} already exist")

    def get_all_groups(self, db: Session):
        all_groups = self.group_repository.get_all_groups(db)
        if not all_groups:
            raise ValueError(f"No group in the database")
        return all_groups

    def get_group_by_id(self, db: Session, group_id: str):
        group = self.group_repository.get_group_by_id(db, group_id)
        if not group:
            raise KeyError(f"Group with id {group_id} does not exist")
        return group

    def update_group(self, db: Session, id: str, name: str):
        if name not in {group.value for group in GroupType}:
            raise ValueError(
                f"Group with name: {name} must be {GroupType.REGULAR.value} or {GroupType.ADMIN.value}"
            )
        return self.group_repository.update_group(db, id, name)

    def delete_group_by_id(self, db: Session, group_id: str):
        return self.group_repository.delete_group_by_id(db, group_id)
