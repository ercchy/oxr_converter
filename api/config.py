import os
from os.path import abspath, dirname
from pathlib import Path


class Config:
    __ROOT_PATH = Path(__file__).resolve().parent
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ROOT_PATH = __ROOT_PATH
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///{}/zapo.db'.format(ROOT_PATH)) # SQLite, etc.
    MIGRATION_DIR = os.path.join('api', 'migrations')
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/api/zapo.log')

class ProductionConfig(Config):
    DATABASE_URI = '' # MySQL, PostgreSQL, MariaDB, etc.
    ENV = 'production'

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    ENV = 'development'

class TestingConfig(Config):
    TESTING = True