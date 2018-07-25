
from flask_testing import TestCase

from app import app, db


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('config.TestConfig')
        db.init_app(app)
        db.create_all(app=app)
        return app
