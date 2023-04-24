from Sig import db
from uuid import uuid4
from datetime import datetime


def get_uuid():
    return uuid4().hex


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(34), primary_key=True, unique=True, default=get_uuid)
    user_name = db.Column(db.String(345), unique=True, nullable=False)
    email = db.Column(db.String(345), unique=True, nullable=False)
    password = db.COlumn(db.String(), nullable=False)
    api_key = db.Column(db.String(160), nullable=True)
    is_active = db.Colum(db.Boolean(), nullable=False, default=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_name, email, password, api_key=None):
        self.user_name = user_name
        self.email = email
        self.password = password
        self.api_key = api_key

    def __repr__(self):
        return f"user_name({self.user_name}), email({self.email}), is_active({self.is_active}), date_registered({self.date_registered}))"

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()