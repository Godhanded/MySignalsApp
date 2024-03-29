from MySignalsApp import db
from datetime import datetime
from uuid import uuid4


def get_uuid():
    return uuid4().hex


# Create a base model class that will contain common functionality
class BaseModel(db.Model):
    """BaseClass for all models"""

    # Make this class abstract so it won't be mapped to a database table
    __abstract__ = True

    # Define a primary key column with a default value of a generated UUID
    id = db.Column(
        db.String(40), primary_key=True, unique=True, nullable=False, default=get_uuid
    )

    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def insert(self):
        """Insert the current object into the database"""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Update the current object in the database"""
        db.session.commit()

    def delete(self):
        """Delete the current object from the database"""
        db.session.delete(self)
        db.session.commit()

    def format(self):
        """Format the object's attributes as a dictionary"""
        # This method should be overridden in subclasses
        raise NotImplementedError("Subclasses must implement the 'format' method")
