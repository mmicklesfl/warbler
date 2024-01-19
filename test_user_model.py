"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
import unittest
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        self.client = app.test_client()

        with self.client:
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
        with self.client:
            with app.app_context():
                db.session.remove()
                db.drop_all()
            return super().tearDown()

    def test_user_model(self):
        """Does basic model work?"""
        with self.client:
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
            user = User(email="test_repr@test.com", username="testrepr", password="HASHED_PASSWORD")
            db.session.add(user)
            db.session.commit()

            self.assertEqual(repr(user), f'<User #{user.id}: {user.username}, {user.email}>')

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        with app.app_context():
            user1 = User.signup("user5", "user5@test.com", "password", None)
            user2 = User.signup("user6", "user6@test.com", "password", None)
            db.session.add_all([user1, user2])
            db.session.commit()

            user1.followers.append(user2)
            db.session.commit()

            self.assertTrue(user1.is_followed_by(user2))
            self.assertFalse(user2.is_followed_by(user1))

    def test_is_not_followed_by(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""
        with app.app_context():
            user1 = User.signup("user7", "user7@test.com", "password", None)
            user2 = User.signup("user8", "user8@test.com", "password", None)
            db.session.add_all([user1, user2])
            db.session.commit()

            self.assertFalse(user1.is_followed_by(user2))
     

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        with app.app_context():
            user1 = User.signup("user1", "user1@test.com", "password", None)
            user2 = User.signup("user2", "user2@test.com", "password", None)
            db.session.add_all([user1, user2])
            db.session.commit()

            user1.following.append(user2)
            db.session.commit()

            self.assertTrue(user1.is_following(user2))
            self.assertFalse(user2.is_following(user1))

    def test_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""
        with app.app_context():
            user1 = User.signup("user3", "user3@test.com", "password", None)
            user2 = User.signup("user4", "user4@test.com", "password", None)
            db.session.add_all([user1, user2])
            db.session.commit()

            self.assertFalse(user1.is_following(user2))


    def test_user_create(self):
        """Does User.create successfully create a new user given valid credentials?"""
        with self.client:
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
        with self.client:
            with app.app_context():
                invalid = User.signup(None, "test@test.com", "password", None)
                uid = 123456789
                invalid.id = uid
                with self.assertRaises(exc.IntegrityError):
                    db.session.commit()

    def test_valid_authentication(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        with self.client:
            with app.app_context():
                u = User.authenticate(self.u.username, "password")
                self.assertIsNotNone(u)
                self.assertEqual(u.id, self.uid)

    def test_invalid_username_authentication(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        with self.client:
            with app.app_context():
                self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password_authentication(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        with self.client:
            with app.app_context():
                self.assertFalse(User.authenticate(self.u.username, "badpassword"))


if __name__ == '__main__':
    unittest.main()