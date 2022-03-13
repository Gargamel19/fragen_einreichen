from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from app import login
from app.extentions import db


@login.user_loader
def load_user(aid):
    return User.query.get(int(aid))


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, username):
        self.username = username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.commit()


class Question(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(128))
    answer = db.Column(db.String(128))
    kategory = db.Column(db.String(128))
    username = db.Column(db.String(128))

    def __init__(self, question, answer, kategory, username):
        self.username = username
        self.kategory = kategory
        self.question = question
        self.answer = answer

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.commit()

