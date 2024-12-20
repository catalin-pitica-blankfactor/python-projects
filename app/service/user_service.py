import json

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.model.user_model import User
from app.repository.user_repository import UserRepository
import httpx


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def add_new_user(
        self,
        db: Session,
        user_name: str,
        user_group: str,
        background_task: BackgroundTasks,
    ):
        exist_user = self.user_repository.get_user_by_name(db, user_name)
        if exist_user:
            raise ValueError(
                f"User with name: {user_name} already exist in the database"
            )
        new_user = self.user_repository.create_user(db, user_name, user_group)
        background_task.add_task(
            self.process_content,
            user_id=new_user.uuid,
            db=db,
            url="https://api.github.com/",
        )
        return new_user

    async def process_content(self, user_id: str, db: Session, url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            file_content = response.text
        replaced_placeholder = file_content.replace("{user}", user_id)
        self.user_repository.update_user_url(db, user_id, replaced_placeholder)

    def get_all_users(self, db: Session):
        users = self.user_repository.get_all_users(db)
        if not users:
            raise ValueError(f"No user in the database")
        response = []
        for user in users:
            response.append(
                (
                    {
                        "uuid": user.uuid,
                        "name": user.name,
                        "group_name": [group.name for group in user.group],
                        "url": json.loads(user.urls),
                    }
                )
            )
        return response

    def get_user_by_id(self, db: Session, user_id: str):
        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise KeyError(f"User with id: {user_id} does not exist in the database")
        response = {
            "uuid": user.uuid,
            "name": user.name,
            "group_name": [group.name for group in user.group],
            "url": json.loads(user.urls),
        }
        return response

    def check_user_validation(self, db: Session, user_id: str):
        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise KeyError(f"User with id {user_id} does not exist")
        return user

    def check_group_in_user(self, db: Session, user: User, group_name: str):
        group_name_from_user = [group.name for group in user.group]
        if group_name not in group_name_from_user:
            raise ValueError(
                f"Group {group_name} does not part of the user id {user.uuid}"
            )

    def update_user(self, db: Session, user_id: str, user_name: str):
        user = self.user_repository.update_user(db, user_id, user_name)
        response = {
            "uuid": user.uuid,
            "name": user.name,
            "group_name": [group.name for group in user.group],
            "url": json.loads(user.urls),
        }
        return response

    def delete_user_by_id(self, db: Session, user_id: str):
        return self.user_repository.delete_user(db, user_id)
