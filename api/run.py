from flask import Flask
from flask_migrate import Migrate

from .config import *
from .models.database import db, ma
from .cache.redis import redis
from .controllers import v1_routes, error_routes
from .utils.request_utils import RequestFormatter
from .utils.middleware import LoggingMiddleware

import logging

# App init
application = Flask(__name__)
application.config.from_object(DevelopmentConfig)
application.wsgi_app = LoggingMiddleware(application.wsgi_app)

# Database and Marshmallow init
# Marshmallow is a serializer
db.init_app(application)
ma.init_app(application)

# Data migrations setup (not sure about this)
migrate = Migrate(application, db, directory=DevelopmentConfig.MIGRATION_DIR)

# Redis
redis.init_app(application)

# Blueprint register
# We added this so we can change the application layout structure
application.register_blueprint(v1_routes.bp, url_prefix='/api/v1')
application.register_blueprint(error_routes.bp)

# setting logger
formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)
handler = logging.FileHandler(DevelopmentConfig.LOG_FILE)
handler.setFormatter(formatter)
logger = logging.getLogger('werkzeug')
logger.addHandler(handler)
application.logger.addHandler(handler)