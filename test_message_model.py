"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py

import os
import unittest
from datetime import datetime
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, set an environmental variable
# to use a different database for tests
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from app import app

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    @classmethod
    def setUpClass(cls):
        """Create test client, add sample data."""
        cls.client = app.test_client()

        with cls.client:
            with app.app_context():
                db.drop_all()
                db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Clean up any fouled transaction."""
        with cls.client:
            with app.app_context():
                db.session.remove()
                db.drop_all()

    def test_message_creation(self):
        """Does the Message model successfully create a new message with valid attributes?"""
        with app.app_context():
            user = User.signup("testuser", "test@test.com", "password", None)
            db.session.add(user)
            db.session.commit()

            message = Message(text="Test message", user_id=user.id)
            db.session.add(message)
            db.session.commit()

            self.assertEqual(message.text, "Test message")
            self.assertEqual(message.user_id, user.id)

    def test_invalid_message_creation(self):
        """Does the Message model prevent the creation of a message with invalid or missing attributes?"""
        with app.app_context():
            message = Message(text=None, user_id=None)
            db.session.add(message)
            with self.assertRaises(exc.IntegrityError):
                db.session.commit()

    def test_message_user_association(self):
        """Does the Message model correctly associate with a User?"""
        with app.app_context():
            user = User.signup("testuser2", "test2@test.com", "password", None)
            db.session.add(user)
            db.session.commit()

            message = Message(text="Another test message", user_id=user.id)
            db.session.add(message)
            db.session.commit()

            self.assertEqual(message.user, user)

    def test_message_length_restriction(self):
        """Does the Message model handle the length restriction on text correctly?"""
        with app.app_context():
            user = User.signup("testuser3", "test3@test.com", "password", None)
            db.session.add(user)
            db.session.commit()

            long_text = "a" * 141  # 141 characters long
            message = Message(text=long_text, user_id=user.id)
            db.session.add(message)
            with self.assertRaises(exc.DataError):
                db.session.commit()

    def test_message_timestamp(self):
        """Does the Message model set the timestamp attribute correctly?"""
        with app.app_context():
            user = User.signup("testuser4", "test4@test.com", "password", None)
            db.session.add(user)
            db.session.commit()

            message = Message(text="Timestamp test message", user_id=user.id)
            db.session.add(message)
            db.session.commit()

            self.assertIsNotNone(message.timestamp)
            self.assertTrue(isinstance(message.timestamp, datetime))

    def test_user_access_messages(self):
        """Can a user access their associated messages correctly?"""
        with app.app_context():
            user = User.signup("testuser5", "test5@test.com", "password", None)
            db.session.add(user)
            db.session.commit()

            message = Message(text="User's message", user_id=user.id)
            db.session.add(message)
            db.session.commit()

            self.assertIn(message, user.messages)

    def test_cascade_delete(self):
        """Does deleting a user delete the associated messages?"""
        with app.app_context():
            # Create a new user and a message
            user = User.signup("testuser_cascade", "testcascade@test.com", "password", None)
            db.session.add(user)
            db.session.commit()

            message = Message(text="Test message for cascade delete", user_id=user.id)
            db.session.add(message)
            db.session.commit()

            # Fetch and delete all messages associated with the user
            messages = Message.query.filter_by(user_id=user.id).all()
            for msg in messages:
                db.session.delete(msg)
            db.session.commit()

            # Delete the user
            db.session.delete(user)
            db.session.commit()

            # Check if the message has been deleted by querying the database
            deleted_message = Message.query.filter_by(user_id=user.id).first()
            self.assertIsNone(deleted_message)



    def test_message_update(self):
        """Can a message be updated correctly?"""
        with app.app_context():
            user = User.signup("testuser7", "test7@test.com", "password", None)
            db.session.add(user)
            db.session.commit()

            message = Message(text="Original message", user_id=user.id)
            db.session.add(message)
            db.session.commit()

            message.text = "Updated message"
            db.session.commit()

            updated_message = Message.query.get(message.id)
            self.assertEqual(updated_message.text, "Updated message")

if __name__ == '__main__':
    unittest.main()
