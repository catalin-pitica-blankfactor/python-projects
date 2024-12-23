from unittest import TestCase
from unittest.mock import MagicMock, create_autospec, patch
from sqlalchemy.orm import Session


class TestGroupRepository(TestCase):

    db: Session

    mock_group1 = MagicMock()
    mock_group1.uuid = "be2a91c4-df99-490d-9061-bc12f50a80b7"
    mock_group1.name = "regular"

    mock_group2 = MagicMock()
    mock_group2.uuid = "b34d63a3-12fd-456e-b6d7-27c8ab69a6e3"
    mock_group2.name = "admin"

    def setUp(self):

        from app.repository.group_repository import GroupRepository
        from app.model.group_model import Group

        self.db = create_autospec(Session)
        self.Group = Group
        self.groupRepository = GroupRepository()

    def test_get_group_by_id(self):

        mock_query = self.db.query.return_value
        mock_query.filter.return_value.first.return_value = self.mock_group1

        retrieved_group = self.groupRepository.get_group_by_id(
            self.db, self.mock_group1.uuid
        )

        self.db.query.assert_called_once_with(self.Group)
        self.assertEqual(retrieved_group, self.mock_group1)

    def test_get_all_groups(self):

        mock_group = [self.mock_group1, self.mock_group2]
        mock_query = self.db.query.return_value
        mock_query.all.return_value = mock_group

        retrieved_groups = self.groupRepository.get_all_groups(self.db)

        self.db.query.assert_called_once_with(self.Group)
        self.assertEqual(len(retrieved_groups), len(mock_group))
        self.assertEqual(retrieved_groups[0].uuid, self.mock_group1.uuid)
        self.assertEqual(retrieved_groups[1].uuid, self.mock_group2.uuid)

    def test_check_exist_group_name(self):

        mock_query = self.db.query.return_value
        mock_query.filter.return_value.first.return_value = self.mock_group1

        retrieved_group = self.groupRepository.check_exist_group_name(
            self.db, self.mock_group1.name
        )

        self.db.query.assert_called_once_with(self.Group)
        self.assertEqual(retrieved_group, self.mock_group1)

    @patch("uuid.uuid4", return_value="be2a91c4-df99-490d-9061-bc12f50a80b7")
    def test_create_group(self, mock_uuid):

        new_group_name = "regular"

        created_group = self.groupRepository.create_group(self.db, new_group_name)

        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(created_group)

        self.assertEqual(created_group.uuid, self.mock_group1.uuid)
        self.assertEqual(created_group.name, new_group_name)

    def test_update_group(self):

        updated_group_name = "updated_name"

        self.db.query.return_value.filter.return_value.first.return_value = (
            self.mock_group1
        )

        updated_group = self.groupRepository.update_group(
            self.db, self.mock_group1.uuid, updated_group_name
        )

        self.mock_group1.name = updated_group_name
        self.db.query.return_value.filter.return_value.update.assert_called_once_with(
            {self.Group.name: updated_group_name}
        )

        self.db.commit.assert_called_once()
        self.db.query.return_value.filter.return_value.first.assert_called_once()

        self.assertEqual(updated_group.name, updated_group_name)

    def test_delete_group_by_id(self):

        mock_query = self.db.query.return_value
        mock_query.filter.return_value.first.return_value = self.mock_group1

        self.groupRepository.delete_group_by_id(self.db, self.mock_group1.uuid)

        self.db.query.assert_called_once_with(self.Group)
        self.db.delete.assert_called_once_with(self.mock_group1)
        self.db.commit.assert_called_once()
