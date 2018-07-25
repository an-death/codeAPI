__all__ = ['User']

from datetime import datetime

from .abstract_model import db, Model
from .session import Session


class User(Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create_user(cls, email):
        user = cls(email=email)
        session = Session(user=user)
        db.session.add(*[user, session])
        db.session.commit()
        session.token = session.encode_auth_token()
        db.session.add(session)
        db.session.commit()
        return user

    @classmethod
    def get_by_token(cls, token):
        session_id = Session.decode_auth_token(token)
        session = Session.query.get(session_id)
        return session.user

    @property
    def token(self):
        return self.session.token.decode()

    @staticmethod
    def is_exist(**kwargs):
        return User.query.filter_by(**kwargs).count()
