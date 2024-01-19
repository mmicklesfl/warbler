import os
import unittest
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        self.client = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

            self.uid = 1111
            u = User.signup("testuser", "test@test.com", "password", None)
            u.id = self.uid
            db.session.commit()

        self.u = User.query.get(self.uid)

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        return super().tearDown()

    def test_user_model(self):
        """Does basic model work?"""
        with app.app_context():
            u = User(
                email="test@test.com",
                username="testuser",
                password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()

            self.assertEqual(len(u.messages), 0)
            self.assertEqual(len(u.followers), 0)

    def test_user_model_repr(self):
        """Does the repr method work as expected?"""
        with app.app_context():
            self.assertEqual(repr(self.u), f'<User #{self.u.id}: {self.u.username}, {self.u.email}>')

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        with app.app_context():
            u1 = User.query.get(self.uid)
            u2 = User.signup("testuser2", "test2@test.com", "password", None)
            u2.id = 2222
            db.session.add(u2)
            db.session.commit()

            follow = Follows(user_being_followed_id=u2.id, user_following_id=u1.id)
            db.session.add(follow)
            db.session.commit()

            self.assertTrue(u1.is_followed_by(u2))
            self.assertFalse(u2.is_followed_by(u1))


    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        with app.app_context():
            u1 = User.query.get(self.uid)
            u2 = User.signup("testuser2", "test2@test.com", "password", None)
            u2.id = 2222
            db.session.add(u2)
            db.session.commit()

            follow = Follows(user_being_followed_id=u1.id, user_following_id=u2.id)
            db.session.add(follow)
            db.session.commit()

            self.assertTrue(u1.is_following(u2))
            self.assertFalse(u2.is_following(u1))


    def test_user_create(self):
        """Does User.create successfully create a new user given valid credentials?"""
        with app.app_context():
            u = User.signup("testuser3", "test3@test.com", "password", None)
            uid = 3333
            u.id = uid
            db.session.commit()

            u_test = User.query.get(uid)
            self.assertIsNotNone(u_test)
            self.assertEqual(u_test.username, "testuser3")
            self.assertEqual(u_test.email, "test3@test.com")
            self.assertNotEqual(u_test.password, "password")
            self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        """Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""
        with app.app_context():
            invalid = User.signup(None, "test@test.com", "password", None)
            uid = 123456789
            invalid.id = uid
            with self.assertRaises(exc.IntegrityError):
                db.session.commit()

    def test_valid_authentication(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        with app.app_context():
            u = User.authenticate(self.u.username, "password")
            self.assertIsNotNone(u)
            self.assertEqual(u.id, self.uid)

    def test_invalid_username_authentication(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        with app.app_context():
            self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password_authentication(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        with app.app_context():
            self.assertFalse(User.authenticate(self.u.username, "badpassword"))


if __name__ == '__main__':
    unittest.main()