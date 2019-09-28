from sqlalchemy import func, DateTime
from sqlalchemy.event import listens_for

from ..cache import redis
from .database import db, ma

import logging
logger = logging.getLogger('werkzeug')


class ConvertData(db.Model):
    # Self incrementing PK
    id = db.Column(db.Integer, primary_key=True)

    # Passed data
    currency_code = db.Column(db.String(3), nullable=False)
    requested_amount = db.Column(db.DECIMAL(precision=8), nullable=False)

    # Retrived data
    oxr_price = db.Column(db.DECIMAL, nullable=False)

    # Calculated ammount
    final_amount = db.Column(db.DECIMAL(precision=8), nullable=False)

    # Metadata
    date_created = db.Column(DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(DateTime(timezone=True), server_default=func.now())
    request_id = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<ID {self.request_id}>'

# RequestInfo schema
class ConvertDataSchema(ma.Schema):
    class Meta:
        fields = ('currency_code', 'requested_amount', 'oxr_price', 'final_amount', 'date_created', 'date_updated')
# Init schema
convert_data_schema = ConvertDataSchema()


@listens_for(ConvertData, 'after_insert', propagate=True)
def after_insert_function(mapper, connection, target):
    logger.error('Signal was fired: {}', target.id)
    print("work jeba")
    assert target.id is not None
    redis.set('{}:{}:{}'.format(target.currency_code, target.request_id, 1), 1)
