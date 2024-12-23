from unittest import TestCase
from unittest.mock import patch, MagicMock
from app.core.database import get_db


class TestGetDbFunction(TestCase):

    @patch("app.core.database.SessionLocal")
    def test_get_db(self, MockSessionLocal):

        mock_session = MockSessionLocal.return_value

        db_session = next(get_db())

        MockSessionLocal.assert_called_once()
        self.assertEqual(db_session, mock_session)

        mock_session.close.assert_called_once()
