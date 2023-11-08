import os
from unittest import TestCase
from app import app, CURR_USER_KEY
from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup(username="testuser1",
                            email="test@test.com",
                            password="testuser",
                            image_url=None)
        user1.id = 11
        self.user1 = user1

        user2 = User.signup("testuser2", "test1@test.com", "password", None)
        user2.id = 22
        self.user2 = user2

        user3 = User.signup("username3", "test2@test.com", "password", None)
        user3.id = 33
        self.user3 = user3

        user4 = User.signup("username4", "test3@test.com", "password", None)
        self.user4 = user4

        db.session.commit()

    def setup_messages(self):
        m1 = Message(id=100, text="Happy Friday", user_id=self.user1.id)
        self.m1 = m1

        m2 = Message(text="Great app", user_id=self.user1.id)
        self.m2 = m2

        m3 = Message(id=99, text="Warble is fun", user_id=self.user2.id)
        self.m3 = m3

        db.session.add_all([m1, m2, m3])
        db.session.commit()

        like = Likes(user_id=self.user3.id, message_id=self.m1.id)

        db.session.add(like)
        db.session.commit()

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.user1.id,
                     user_following_id=self.user2.id)
        f2 = Follows(user_being_followed_id=self.user2.id,
                     user_following_id=self.user3.id)
        f3 = Follows(user_being_followed_id=self.user3.id,
                     user_following_id=self.user1.id)

        db.session.add_all([f1, f2, f3])
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_list_users(self):
        with app.test_client() as client:
            resp = client.get("/users")

            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", html)
            self.assertIn("@testuser2", html)

    def test_list_users_search(self):
        with app.test_client() as client:
            resp = client.get("/users?q=test")
            html = resp.get_data(as_text=True)

            self.assertIn("@testuser1", html)
            self.assertIn("@testuser2", html)

            self.assertNotIn("@username3", html)
            self.assertNotIn("@username4", html)

    def test_users_show(self):
        self.setup_messages()
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user1.id}")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", html)
            self.assertIn(self.m1.text, html)
            self.assertNotIn(self.m3.text, html)

    def test_handle_likes_add(self):
        self.setup_messages()
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            resp = client.post(
                f"/users/add_like/{self.m3.id}", follow_redirects=True)
            like = Likes.query.filter(Likes.message_id == self.m3.id).all()

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(like), 1)

    def test_handle_likes_remove(self):
        self.setup_messages()
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user3.id
            resp = client.post(
                f"/users/add_like/{self.m1.id}", follow_redirects=True)
            all_likes = Likes.query.filter(
                Likes.message_id == self.m1.id).all()

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(all_likes), 0)

    def test_user_show_follows(self):
        self.setup_followers()
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            resp = client.get(
                f"/users/{self.user1.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"@{self.user2.username}", html)

    def test_user_show_following(self):
        self.setup_followers()
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            resp = client.get(
                f"/users/{self.user1.id}/following", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"@{self.user3.username}", html)
