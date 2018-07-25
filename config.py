# coding: utf8
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    PROD = 'production'
    TEST = 'test'
    DEV = 'development'

    def __new__(cls):
        env = os.environ.get('FLASK_ENV')
        if env == cls.DEV:
            return DevConfig
        elif env == cls.TEST:
            return TestConfig
        elif env == cls.PROD:
            return ProdConfig
        raise EnvironmentError('Environment variable not configured')


class BaseConfig:
    SECRET_KEY = 'some_key'
    EXP_SEC = 30
    CODE_LENGTH = 4
    MAX_CODES_LIMIT = 10


class DevConfig(BaseConfig):
    DEBUG = 1
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "dev.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_AUTOFLUSH = False
    SQLALCHEMY_DATABASE_URI = f'sqlite://'


class ProdConfig(BaseConfig):
    pass
