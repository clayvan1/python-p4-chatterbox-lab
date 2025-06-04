from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define the Message model
class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages' # Set the table name

    id = db.Column(db.Integer, primary_key=True) # Primary key
    body = db.Column(db.String, nullable=False) # Message content, cannot be null
    username = db.Column(db.String, nullable=False) # Username, cannot be null
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # Timestamp for creation
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow) # Timestamp for last update

    # Serialization rules to control JSON output
    # No specific rules needed for this simple model, but good to keep in mind
    # serialize_rules = () # Example if you needed to exclude fields

    def __repr__(self):
        return f'<Message {self.id}: {self.body[:20]}... by {self.username}>'

