from pathlib import Path

class Config:
    __ROOT_PATH = Path(__file__).resolve().parent
    DEBUG = False
    TESTING = False
    SECRET_KEY = b'D\x12\xeb\xe2b\xc3.\x94\xc7\xe4\x03\xb0\xffE\xbe\x10' # Change to a new KEY!
    ROOT_PATH = __ROOT_PATH
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{ROOT_PATH}/test.db' # SQLite, etc.

class ProductionConfig(Config):
    DATABASE_URI = '' # MySQL, PostgreSQL, MariaDB, etc.

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    ENV = 'development'

class TestingConfig(Config):
    TESTING = True