from app import db
from datetime import datetime
from app import login
from flask_login import UserMixin

from hashlib import sha256
from uuid import uuid4

def hash_password(password):
    # uuid is used to generate a random number
    # salt is used in order to prevent dictionary attacks and rainbow tables attacks
    return sha256(password.encode()).hexdigest()


def check_password(hashed_password, user_password):
    password = hashed_password
    return password == sha256(user_password.encode()).hexdigest()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password = hash_password(password)

    def check_password(self, password):
        return check_password(self.password, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User_games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, index=True)
    user_rating = db.Column(db.DECIMAL(10,2))
    added_at = db.Column(db.TIMESTAMP(), default=datetime.utcnow)

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(10000))
    released = db.Column(db.String(255))
    background_image = db.Column(db.String(255))
    url = db.Column(db.String(255))
    rating = db.Column(db.DECIMAL(10,2))
    achiev_count = db.Column(db.Integer)

    def __repr__(self):
        return '<Games {}>'.format(self.body)


