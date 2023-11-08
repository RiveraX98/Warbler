"""User model tests."""

from app import app
import os
from unittest import TestCase
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        u1.id = 1111
        u2 = User.signup("test2", "email2@email.com", "password", None)
        u2.id = 2222

        u1 = User.query.get(u1.id)
        u2 = User.query.get(u2.id)

        db.session.commit()

        self.u1 = u1
        self.u2 = u2

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    # Following tests:

    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    # Signup Tests:

    def test_signup(self):
        u3 = User.signup("testtesttest", "testtest@test.com", "password", None)
        u3.id = 3333

        db.session.commit()

        u_test = User.query.get(3333)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")

    # Authentication Tests

    def test_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u1.id)

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))
