import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch, create_autospec, AsyncMock
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.model import User, Group


class TestUserService(TestCase):

    db: Session

    @patch("app.service.user_service.UserRepository")
    def setUp(self, MockUserRepository):

        from app.service.user_service import UserService

        self.db = create_autospec(Session)
        self.mock_user_repository = MockUserRepository.return_value
        self.UserService = UserService()
        self.UserService.user_repository = self.mock_user_repository
        self.mock_background_task = MagicMock(spec=BackgroundTasks)

        self.mock_user1 = MagicMock(spec=User)
        self.mock_user1.uuid = "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3"
        self.mock_user1.name = "catalin"
        self.mock_user1.urls = '{"current_user_url": "https://api.github.com/user"}'
        self.mock_user1.group = [MagicMock()]
        self.mock_user1.group[0].name = "regular"

        self.mock_user2 = MagicMock(spec=User)
        self.mock_user2.uuid = "d9bc8265-8abc-406c-aee2-2a3584431d5e"
        self.mock_user2.name = "iulia"
        self.mock_user2.urls = '{"current_user_url": "https://api.github.com/user"}'
        self.mock_user2.group = [MagicMock()]
        self.mock_user2.group[0].name = "regular"

        self.mock_group = MagicMock(spec=Group)
        self.mock_group.uuid = "be2a91c4-df99-490d-9061-bc12f50a80b7"
        self.mock_group.name = "regular"

    def test_get_user_by_id(self):
        self.mock_user_repository.get_user_by_id.return_value = self.mock_user1

        response = self.UserService.get_user_by_id(self.db, self.mock_user1.uuid)

        self.mock_user_repository.get_user_by_id.assert_called_once_with(
            self.db, self.mock_user1.uuid
        )

        expected_response = {
            "uuid": "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3",
            "name": "catalin",
            "url": {"current_user_url": "https://api.github.com/user"},
            "group_name": ["regular"],
        }
        self.assertEqual(response, expected_response)

    def test_get_user_by_id_not_found(self):

        self.mock_user_repository.get_user_by_id.return_value = None
        non_existing_user_id = "non-existing-uuid"

        with self.assertRaises(KeyError) as context:
            self.UserService.get_user_by_id(self.db, non_existing_user_id)

        self.mock_user_repository.get_user_by_id.assert_called_once_with(
            self.db, non_existing_user_id
        )
        self.assertEqual(
            str(context.exception.args[0]),
            f"User with id: {non_existing_user_id} does not exist in the database",
        )

    def test_get_all_users(self):

        mock_users = [self.mock_user1, self.mock_user2]
        self.mock_user_repository.get_all_users.return_value = mock_users

        response = self.UserService.get_all_users(self.db)

        self.mock_user_repository.get_all_users.assert_called_once_with(self.db)

        expected_response = [
            {
                "uuid": "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3",
                "name": "catalin",
                "group_name": ["regular"],
                "url": {"current_user_url": "https://api.github.com/user"},
            },
            {
                "uuid": "d9bc8265-8abc-406c-aee2-2a3584431d5e",
                "name": "iulia",
                "group_name": ["regular"],
                "url": {"current_user_url": "https://api.github.com/user"},
            },
        ]
        self.assertEqual(response, expected_response)

    def test_get_all_users_no_user_in_database(self):

        self.mock_user_repository.get_all_users.return_value = None

        with self.assertRaises(ValueError) as context:
            self.UserService.get_all_users(self.db)

        self.mock_user_repository.get_all_users.assert_called_once_with(self.db)
        self.assertEqual(str(context.exception.args[0]), f"No user in the database")

    def test_check_user_validation_success(self):

        self.mock_user_repository.get_user_by_id.return_value = self.mock_user1
        result = self.UserService.check_user_validation(self.db, self.mock_user1.uuid)
        self.mock_user_repository.get_user_by_id.assert_called_once_with(
            self.db, self.mock_user1.uuid
        )
        self.assertEqual(result, self.mock_user1)

    def test_check_user_validation_fails(self):

        self.mock_user_repository.get_user_by_id.return_value = None

        with self.assertRaises(KeyError) as context:
            self.UserService.check_user_validation(self.db, "non-existing-uuid")

        self.mock_user_repository.get_user_by_id.assert_called_once_with(
            self.db, "non-existing-uuid"
        )
        self.assertEqual(
            context.exception.args[0], "User with id non-existing-uuid does not exist"
        )

    def test_check_group_in_user_success(self):

        self.UserService.check_group_in_user(
            self.db, self.mock_user1, self.mock_group.name
        )
        self.assertTrue(True)

    def test_check_group_in_user_fails(self):

        with self.assertRaises(ValueError) as context:
            self.UserService.check_group_in_user(
                self.db, self.mock_user1, "non-existing-group"
            )

        self.assertEqual(
            context.exception.args[0],
            f"Group non-existing-group does not part of the user id {self.mock_user1.uuid}",
        )

    def test_update_user(self):

        updated_name = "andreea"
        self.mock_user1.name = updated_name
        self.mock_user_repository.update_user.return_value = self.mock_user1

        response = self.UserService.update_user(
            self.db, self.mock_user1.uuid, updated_name
        )
        self.mock_user_repository.update_user.assert_called_once_with(
            self.db, self.mock_user1.uuid, updated_name
        )

        expected_response = {
            "uuid": "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3",
            "name": "andreea",
            "url": {"current_user_url": "https://api.github.com/user"},
            "group_name": ["regular"],
        }

        self.assertEqual(response, expected_response)

    def test_delete_user(self):

        self.mock_user_repository.delete_user.return_value = None

        result = self.UserService.delete_user_by_id(self.db, self.mock_user1.uuid)

        self.assertIsNone(result)

    @patch("app.service.user_service.httpx.AsyncClient")
    def test_process_content(self, MockAsyncClient):

        replace_placeholder = '{"current_user_url": "https://api.github.com/510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3"}'

        mock_client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = '{"current_user_url": "https://api.github.com/{user}"}'
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.get.return_value = mock_response

        MockAsyncClient.return_value = mock_client_instance

        async def run_test():
            await self.UserService.process_content(
                self.mock_user1.uuid, self.db, "https://api.github.com/{user}"
            )

        asyncio.run(run_test())

        MockAsyncClient.assert_called_once()
        mock_client_instance.get.assert_awaited_once_with(
            "https://api.github.com/{user}"
        )

        self.mock_user_repository.update_user_url.assert_called_once_with(
            self.db, self.mock_user1.uuid, replace_placeholder
        )

    def test_add_new_user_success(self):

        self.mock_user_repository.get_user_by_name.return_value = None
        self.mock_user_repository.create_user.return_value = self.mock_user1

        response = self.UserService.add_new_user(
            self.db,
            self.mock_user1.name,
            self.mock_group.name,
            self.mock_background_task,
        )

        self.mock_user_repository.get_user_by_name.assert_called_once_with(
            self.db, self.mock_user1.name
        )
        self.mock_user_repository.create_user.assert_called_once_with(
            self.db, self.mock_user1.name, self.mock_group.name
        )
        self.mock_background_task.add_task.assert_called_once_with(
            self.UserService.process_content,
            user_id=self.mock_user1.uuid,
            db=self.db,
            url="https://api.github.com/",
        )
        self.assertEqual(response, self.mock_user1)

    def test_add_new_user_already_exist(self):

        self.mock_user_repository.get_user_by_name.return_value = self.mock_user1

        with self.assertRaises(ValueError) as context:
            self.UserService.add_new_user(
                self.db,
                self.mock_user1.name,
                self.mock_group.name,
                self.mock_background_task,
            )

        self.assertEqual(
            str(context.exception),
            f"User with name: {self.mock_user1.name} already exist in the database",
        )
        self.mock_user_repository.get_user_by_name.assert_called_once_with(
            self.db, self.mock_user1.name
        )
        self.mock_background_task.add_task.assert_not_called()
