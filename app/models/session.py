import jwt

__all__ = ['Session', 'AuthCode']

import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from app import app
from .abstract_model import Model, db

CONFIG = app.config


class Session(Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref("session", uselist=False))

    def encode_auth_token(self):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=app.config['EXP_SEC']),
            'iat': datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise ValueError('Signature expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid token. Please log in again.')

    def create_code(self):
        if len(self.codes) >= app.config['MAX_CODES_LIMIT']:
            raise ValueError('Max codes for current session reached')

        code = AuthCode(session=self).generate_code()
        self.codes.append(code)
        db.session.add(self)
        db.session.commit()
        return code


class AuthCode(Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    attempts = db.Column(db.Integer, default=0)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    session = db.relationship('Session', backref="codes")

    def generate_code(self, length=CONFIG['CODE_LENGTH']):
        min_range = (10 ** (length - 1)) - 1
        max_range = (10 ** (length)) - 1
        self.code = random.randint(min_range, max_range)
        return self

    def is_code_valid(self, exp_sec=CONFIG['EXP_SEC']):
        now = datetime.utcnow()
        delta = relativedelta(seconds=+exp_sec)
        return self.created + delta > now
