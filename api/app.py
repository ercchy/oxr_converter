from flask import Flask
from flask_migrate import Migrate

from .utils import middleware
from .config import *
from .models.database import db, ma
from .cache.redis import redis
from .controllers import v1_routes, error_routes
from .utils.request_utils import RequestFormatter

import logging

# App init
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.wsgi_app = middleware.LoggingMiddleware(app.wsgi_app)

# Database and Marshmallow init
# Marshmallow is a serializer
db.init_app(app)
ma.init_app(app)

# Data migrations setup (not sure about this)
migrate = Migrate(app, db, directory=DevelopmentConfig.MIGRATION_DIR)

# Redis
redis.init_app(app)

# Blueprint register
# We added this so we can change the app layout structure
app.register_blueprint(v1_routes.bp, url_prefix='/api/v1')
app.register_blueprint(error_routes.bp)

# setting logger
formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)
handler = logging.FileHandler('access.log')
handler.setFormatter(formatter)
logger = logging.getLogger('werkzeug')
logger.addHandler(handler)
app.logger.addHandler(handler)