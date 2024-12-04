from unittest import TestCase
from unittest.mock import create_autospec, patch, MagicMock, ANY

from sqlalchemy.orm import Session




class TestUserRepository(TestCase):
    db: Session

    def setUp(self):
        from app.repository.user_repository import UserRepository
        from app.model.user_model import User

        self.db = create_autospec(Session)
        self.User = User
        self.userRepository = UserRepository()

    def test_get_user_by_id(self):

        mock_user = MagicMock()
        mock_user.uuid = "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3"
        mock_user.name = "catalin"
        mock_user.url = {"current_user_url": "https://api.github.com/user",
                         "hub_url": "https://api.github.com/hub"
                         }

        mock_query = self.db.query.return_value
        mock_query.filter.return_value.first.return_value = mock_user

        retrieved_user = self.userRepository.get_user_by_id(self.db, "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3")

        self.db.query.assert_called_once_with(self.User)
        mock_query.filter.assert_called_once_with(ANY)
        self.assertEqual(retrieved_user.uuid, "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3")
        self.assertEqual(retrieved_user.name, "catalin")
        self.assertDictEqual(retrieved_user.url, {"current_user_url": "https://api.github.com/user",
                         "hub_url": "https://api.github.com/hub"
                         })

    def test_get_user_by_name(self):

        mock_user = MagicMock()
        mock_user.uuid = "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3"
        mock_user.name = "catalin"
        mock_user.url = {"current_user_url": "https://api.github.com/user",
                         "hub_url": "https://api.github.com/hub"
                         }

        mock_query = self.db.query.return_value
        mock_query.filter.return_value.first.return_value = mock_user

        retrieved_user = self.userRepository.get_user_by_name(self.db, "catalin")

        self.db.query.assert_called_once_with(self.User)
        mock_query.filter.assert_called_once_with(ANY)
        self.assertEqual(retrieved_user.uuid, "510a0b32-d4e5-40bb-bc6e-a7ddbd2cacb3")
        self.assertEqual(retrieved_user.name, "catalin")
        self.assertDictEqual(retrieved_user.url, {"current_user_url": "https://api.github.com/user",
                                                  "hub_url": "https://api.github.com/hub"
                                                  })

