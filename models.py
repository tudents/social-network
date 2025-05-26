from time import timezone

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    profile_picture = db.Column(db.String(100))



    class Message(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        content = db.Column(db.Text, nullable=False)
        timestamp = db.Column(db.DateTime, default=datetime.now)

        sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
        receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')