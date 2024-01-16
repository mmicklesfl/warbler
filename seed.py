"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import app, db  # Import the app instance along with db
from models import User, Message, Follows

# Wrap the database operations within an application context
with app.app_context():
    db.drop_all()
    db.create_all()

    # Insert data from 'users.csv'
    with open('generator/users.csv') as users:
        db.session.bulk_insert_mappings(User, DictReader(users))

    # Insert data from 'messages.csv'
    with open('generator/messages.csv') as messages:
        db.session.bulk_insert_mappings(Message, DictReader(messages))

    # Insert data from 'follows.csv'
    with open('generator/follows.csv') as follows:
        db.session.bulk_insert_mappings(Follows, DictReader(follows))

    db.session.commit()
