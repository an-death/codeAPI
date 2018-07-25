from flask import current_app
from flask_testing import TestCase

import config
from app import app


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('config.DevConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['SECRET_KEY'] == 'some_key')
        self.assertEqual(app.config['EXP_SEC'], 30)
        self.assertFalse(current_app is None)


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object(config.TestConfig())
        return app

    def test_app_is_testing(self):
        self.assertFalse(app.config['DEBUG'])
        self.assertTrue(app.config['SECRET_KEY'] == 'some_key')
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite://')
