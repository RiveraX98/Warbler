import os
from unittest import TestCase
from app import app, CURR_USER_KEY
from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
app.config['WTF_CSRF_ENABLED'] = False


class UserModelTestCase(TestCase):
    def setUp(self):

        db.drop_all()
        db.create_all()

        user1 = User.signup("testing", "testing@test.com", "password", None)
        user1.id = 11

        db.session.commit()

        self.user1 = User.query.get(user1.id)

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):

        message = Message(
            text="Testing Message",
            user_id=self.user1.id
        )

        db.session.add(message)
        db.session.commit()

        self.assertEqual(len(self.user1.messages), 1)
        self.assertEqual(self.user1.messages[0].text, "Testing Message")

    def test_message_likes(self):
        m1 = Message(
            text="Testing Message",
            user_id=self.user1.id
        )

        user2 = User.signup("User2Test", "test2@email.com", "password", None)
        user2.id = 22
        db.session.add_all([m1, user2])
        db.session.commit()

        user2.likes.append(m1)

        db.session.commit()

        like = Likes.query.filter(Likes.user_id == user2.id).all()
        self.assertEqual(len(like), 1)
        self.assertEqual(like[0].message_id, m1.id)
