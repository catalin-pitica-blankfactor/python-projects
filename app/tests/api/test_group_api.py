from unittest import TestCase
from unittest.mock import MagicMock, create_autospec

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from fastapi.testclient import TestClient

from app.service.group_service import GroupService


client = TestClient(app)


class TestGroupAPI(TestCase):
    db: Session

    def setUp(self):

        self.db = create_autospec(Session)
        self.mock_group_service = MagicMock(spec=GroupService)

        app.dependency_overrides[GroupService] = lambda: self.mock_group_service
        app.dependency_overrides[get_db] = lambda: self.db

        self.group1 = {
            "uuid": "be2a91c4-df99-490d-9061-bc12f50a80b7",
            "name": "regular",
        }

        self.group2 = {
            "uuid": "b34d63a3-12fd-456e-b6d7-27c8ab69a6e3",
            "name": "admin",
        }

    def tearDown(self):
        app.dependency_overrides = {}

    def test_create_group(self):

        self.mock_group_service.add_new_group.return_value = self.group1
        self.mock_group_service.check_existing_group_name.return_value = None

        response = client.post("/group", json={"name": "regular"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"uuid": self.group1["uuid"]})
        self.mock_group_service.check_existing_group_name.assert_called_once_with(
            self.db, "regular"
        )
        self.mock_group_service.add_new_group.assert_called_once_with(
            self.db, "regular"
        )

    def test_create_group_value_error_when_group_name_already_exists(self):
        self.mock_group_service.check_existing_group_name.side_effect = ValueError(
            "Group name already exists"
        )

        response = client.post("/group", json={"name": "duplicate-group"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Group name already exists"})
        self.mock_group_service.check_existing_group_name.assert_called_once_with(
            self.db, "duplicate-group"
        )

        self.mock_group_service.add_new_group.assert_not_called()

        print(
            "Mock Calls to check_existing_group_name:",
            self.mock_group_service.check_existing_group_name.mock_calls,
        )
        print(
            "Mock Calls to add_new_group:",
            self.mock_group_service.add_new_group.mock_calls,
        )

    def test_create_group_already_exist(self):

        self.mock_group_service.check_existing_group_name.side_effect = KeyError(
            "Group already exists"
        )

        response = client.post("/group", json={"name": "regular"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Group already exists"})

        self.mock_group_service.check_existing_group_name.assert_called_once_with(
            self.db, "regular"
        )
        self.mock_group_service.add_new_group.assert_not_called()

    def test_get_all_groups_success(self):

        self.mock_group_service.get_all_groups.return_value = [self.group1, self.group2]

        response = client.get("/group")

        self.assertEqual(response.status_code, 200)

        expected_response = [
            {"uuid": "be2a91c4-df99-490d-9061-bc12f50a80b7", "name": "regular"},
            {"uuid": "b34d63a3-12fd-456e-b6d7-27c8ab69a6e3", "name": "admin"},
        ]
        self.assertEqual(response.json(), expected_response)
        self.mock_group_service.get_all_groups.assert_called_once()

    def test_get_all_groups_no_groups(self):

        self.mock_group_service.get_all_groups.side_effect = ValueError(
            "No group found"
        )

        response = client.get("/group")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "No group found"})

        self.mock_group_service.get_all_groups.assert_called_once_with(self.db)

    def test_get_group_by_id(self):

        self.mock_group_service.get_group_by_id.return_value = self.group1

        response = client.get(f"/group/{self.group1['uuid']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.group1)
        self.mock_group_service.get_group_by_id.assert_called_once_with(
            self.db, self.group1["uuid"]
        )

    def test_get_group_by_id_not_found(self):

        self.mock_group_service.get_group_by_id.side_effect = KeyError(
            "Group not found"
        )

        response = client.get("/group/non-existing-id")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Group not found"})

        self.mock_group_service.get_group_by_id.assert_called_once_with(
            self.db, "non-existing-id"
        )

    def test_update_group(self):

        updated_group = {"uuid": self.group1["uuid"], "name": "updated-regular"}
        self.mock_group_service.get_group_by_id.return_value = self.group1
        self.mock_group_service.update_group.return_value = updated_group

        response = client.put(
            f"/group/{self.group1['uuid']}", json={"name": "updated-regular"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"uuid": updated_group["uuid"]})
        self.mock_group_service.get_group_by_id.assert_called_once_with(
            self.db, self.group1["uuid"]
        )
        self.mock_group_service.update_group.assert_called_once_with(
            self.db, self.group1["uuid"], "updated-regular"
        )

    def test_update_group_raises_value_error_when_group_name_already_exists(self):
        group_id = "1234-abcd"
        updated_name = "new-group-name"
        self.mock_group_service.get_group_by_id.return_value = {
            "uuid": group_id,
            "name": "old-group-name",
        }
        self.mock_group_service.check_existing_group_name.side_effect = ValueError(
            "Group name already exists"
        )

        response = client.put(f"/group/{group_id}", json={"name": updated_name})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Group name already exists"})
        self.mock_group_service.get_group_by_id.assert_called_once_with(
            self.db, group_id
        )
        self.mock_group_service.check_existing_group_name.assert_called_once_with(
            self.db, updated_name
        )

    def test_update_group_not_found(self):

        self.mock_group_service.get_group_by_id.side_effect = KeyError(
            "Group not found"
        )

        response = client.put(
            f"/group/{self.group1['uuid']}", json={"name": "updated-regular"}
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Group not found"})
        self.mock_group_service.get_group_by_id.assert_called_once_with(
            self.db, self.group1["uuid"]
        )

    def test_delete_group_by_id(self):

        self.mock_group_service.get_group_by_id.return_value = self.group1
        self.mock_group_service.delete_group_by_id.return_value = None

        response = client.delete(f"/group/{self.group1['uuid']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), None)
        self.mock_group_service.get_group_by_id.assert_called_once_with(
            self.db, self.group1["uuid"]
        )
        self.mock_group_service.delete_group_by_id.assert_called_once_with(
            self.db, self.group1["uuid"]
        )

    def test_delete_group_by_id_not_found(self):

        self.mock_group_service.get_group_by_id.side_effect = KeyError(
            "Group not found"
        )

        response = client.delete("/group/non-existing-uuid")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Group not found"})
        self.mock_group_service.get_group_by_id.assert_called_once_with(
            self.db, "non-existing-uuid"
        )
