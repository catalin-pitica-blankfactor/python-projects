from unittest import TestCase
from unittest.mock import MagicMock, create_autospec
from fastapi import BackgroundTasks
from pydantic import ValidationError
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.core.database import get_db
from app.main import app
from app.schemas.user_schema import UserResponseForGet
from app.service.group_service import GroupService
from app.service.user_service import UserService

client = TestClient(app)


class TestUserApi(TestCase):

    db: Session

    def setUp(self):

        self.mock_user_service = MagicMock(spec=UserService)
        self.mock_group_service = MagicMock(spec=GroupService)
        app.dependency_overrides[UserService] = lambda: self.mock_user_service
        app.dependency_overrides[GroupService] = lambda: self.mock_group_service
        self.mock_db = create_autospec(Session)
        app.dependency_overrides[get_db] = lambda: self.mock_db

        self.validation_error = MagicMock()
        self.mock_background_task = MagicMock(spec=BackgroundTasks)
        app.dependency_overrides[BackgroundTasks] = lambda: self.mock_background_task
        self.user1 = {
            "uuid": "e1e2e3e4-5678-1234-abcd-5678e1234567",
            "name": "catalin",
            "group_name": ["regular"],
            "url": {"current_user_url": "https://api.github.com/user"},
        }

    def tearDown(self):

        app.dependency_overrides = {}

    def test_create_user_success(self):

        self.mock_group_service.get_group_by_id.return_value = {
            "uuid": "d9bc8265-8abc-406c-aee2-2a3584431d5e"
        }
        self.mock_user_service.add_new_user.return_value = {"uuid": self.user1["uuid"]}

        response = client.post(
            "/user",
            json={
                "user_name": "catalin",
                "user_group": "d9bc8265-8abc-406c-aee2-2a3584431d5e",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"uuid": self.user1["uuid"]})

        self.mock_group_service.get_group_by_id.assert_called_once_with(
            self.mock_db, "d9bc8265-8abc-406c-aee2-2a3584431d5e"
        )
        self.mock_user_service.add_new_user.assert_called_once()

        called_args = self.mock_user_service.add_new_user.call_args
        self.assertEqual(called_args[0][0], self.mock_db)
        self.assertEqual(called_args[0][1], "catalin")
        self.assertEqual(called_args[0][2], "d9bc8265-8abc-406c-aee2-2a3584431d5e")
        self.assertIsInstance(called_args[0][3], BackgroundTasks)

    def test_create_user_value_error(self):

        self.mock_group_service.get_group_by_id.return_value = {
            "uuid": "d9bc8265-8abc-406c-aee2-2a3584431d5e"
        }
        self.mock_user_service.add_new_user.side_effect = ValueError(
            "Invalid user details provided"
        )

        response = client.post(
            "/user",
            json={
                "user_name": "catalin",
                "user_group": "d9bc8265-8abc-406c-aee2-2a3584431d5e",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Invalid user details provided"})

        self.mock_group_service.get_group_by_id.assert_called_once_with(
            self.mock_db, "d9bc8265-8abc-406c-aee2-2a3584431d5e"
        )
        self.mock_user_service.add_new_user.assert_called_once()

        called_args = self.mock_user_service.add_new_user.call_args
        self.assertEqual(called_args[0][0], self.mock_db)
        self.assertEqual(called_args[0][1], "catalin")
        self.assertEqual(called_args[0][2], "d9bc8265-8abc-406c-aee2-2a3584431d5e")
        self.assertIsInstance(called_args[0][3], BackgroundTasks)

    def test_create_user_group_not_found(self):

        self.mock_group_service.get_group_by_id.side_effect = KeyError(
            "Group not found"
        )

        response = client.post(
            "/user",
            json={"user_name": "catalin", "user_group": "invalid-group-id"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Group not found"})

        self.mock_user_service.add_new_user.assert_not_called()

        self.mock_group_service.get_group_by_id.assert_called_once_with(
            self.mock_db, "invalid-group-id"
        )

    def test_get_all_users_success(self):

        self.mock_user_service.get_all_users.return_value = [self.user1]

        response = client.get("/user")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [self.user1])

        self.mock_user_service.get_all_users.assert_called_once_with(self.mock_db)

    def test_get_all_users_value_error(self):

        self.mock_user_service.get_all_users.side_effect = ValueError("No users found")

        response = client.get("/user")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "No users found"})

        self.mock_user_service.get_all_users.assert_called_once_with(self.mock_db)

    def test_get_all_users_validation_error(self):

        try:

            UserResponseForGet(uuid="e1e2e3e4-5678-1234-abcd-5678e1234567")
        except ValidationError as validation_error_instance:
            self.mock_user_service.get_all_users.side_effect = validation_error_instance

        response = client.get("/user")

        self.assertEqual(response.status_code, 400)

        error_details = response.json()["detail"]

        self.assertIn("group_name", str(error_details))
        self.mock_user_service.get_all_users.assert_called_once_with(self.mock_db)

    def test_get_user_by_id_success(self):

        self.mock_user_service.get_user_by_id.return_value = self.user1

        response = client.get(f"/user/{self.user1['uuid']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.user1)

        self.mock_user_service.get_user_by_id.assert_called_once_with(
            self.mock_db, self.user1["uuid"]
        )

    def test_get_user_by_id_not_found(self):

        self.mock_user_service.get_user_by_id.side_effect = KeyError("User not found")

        response = client.get("/user/non-existent-id")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User not found"})

        self.mock_user_service.get_user_by_id.assert_called_once_with(
            self.mock_db, "non-existent-id"
        )

    def test_update_user_success(self):

        self.mock_user_service.check_user_validation.return_value = self.user1
        self.mock_user_service.update_user.return_value = self.user1

        response = client.put(
            f"/user/{self.user1['uuid']}",
            json={"group_name": "regular", "user_name": "Updated John"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.user1)

        self.mock_user_service.check_user_validation.assert_called_once_with(
            self.mock_db, self.user1["uuid"]
        )
        self.mock_user_service.update_user.assert_called_once()

    def test_update_user_not_found(self):

        self.mock_user_service.check_user_validation.side_effect = KeyError(
            "User not found"
        )

        user_update_payload = {
            "group_name": "non-existing-group",
            "user_name": "updated-user",
        }
        response = client.put(f"/user/{self.user1['uuid']}", json=user_update_payload)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User not found"})
        self.mock_user_service.check_user_validation.assert_called_once_with(
            self.mock_db, self.user1["uuid"]
        )

    def test_update_user_group_not_part_of_user(self):

        self.mock_user_service.check_user_validation.return_value = self.user1

        self.mock_user_service.check_group_in_user.side_effect = ValueError(
            "Group non-existing-group does not belong to the user"
        )

        user_update_payload = {
            "group_name": "non-existing-group",
            "user_name": "updated-user",
        }
        response = client.put(f"/user/{self.user1['uuid']}", json=user_update_payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"detail": "Group non-existing-group does not belong to the user"},
        )
        self.mock_user_service.check_user_validation.assert_called_once_with(
            self.mock_db, self.user1["uuid"]
        )
        self.mock_user_service.check_group_in_user.assert_called_once_with(
            self.mock_db, self.user1, "non-existing-group"
        )

    def test_delete_user_by_id_success(self):

        response = client.delete(f"/user/{self.user1['uuid']}")

        self.assertEqual(response.status_code, 200)

        self.mock_user_service.delete_user_by_id.assert_called_once_with(
            self.mock_db, self.user1["uuid"]
        )

    def test_delete_user_not_found(self):

        self.mock_user_service.delete_user_by_id.side_effect = KeyError(
            "User not found"
        )

        response = client.delete("/user/non-existent-id")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "User not found"})

        self.mock_user_service.delete_user_by_id.assert_called_once_with(
            self.mock_db, "non-existent-id"
        )
