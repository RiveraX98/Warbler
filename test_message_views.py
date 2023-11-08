"""Message View tests."""

from app import app, CURR_USER_KEY
import os
from unittest import TestCase
from models import db, connect_db, Message, User
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()

        user1 = User.signup("testuser", "test@test.com", "testuser", None)
        user1.id = 11
        db.session.commit()

        self.user1 = user1

    def tearDown(self):
        db.session.rollback()

    def test_messages_add(self):

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = client.post(
                "/messages/new", data={"text": "Hello World"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello World")
            self.assertIn(f"{msg.text}", html)

    def test_message_destroy(self):

        message = Message(
            id=22,
            text="a test message",
            user_id=self.user1.id
        )
        db.session.add(message)
        db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = client.post("/messages/22/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            m = Message.query.get(22)
            self.assertEqual(resp.status_code, 200)
            self.assertIsNone(m)
            self.assertNotIn(message.text, html)
