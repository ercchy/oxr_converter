from flask import json

from sqlalchemy import func, DateTime
from sqlalchemy.event import listens_for

from ..utils.data_utils import datetime_converter
from ..cache.redis import redis
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

    @property
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<ID {self.request_id}>'


# RequestInfo schema
class ConvertDataSchema(ma.ModelSchema):
    class Meta:
        model = ConvertData

converted_data_schema = ConvertDataSchema()
converted_datas_schema = ConvertDataSchema(many=True)

@listens_for(ConvertData, 'after_insert', propagate=True)
def after_insert_function(mapper, connection, target):
    assert target.id is not None
    logger.info('Event after_insert for ConvertData model was fired: {}'.format(target.request_id))
    # Surely there is a better way than this?
    cleaned_data = target.to_dict
    json.dumps(cleaned_data, default = datetime_converter)
    jsoned_entry = json.dumps(cleaned_data, use_decimal=True, default = datetime_converter)
    # TODO: Error handle
    redis.zadd('{}'.format(target.currency_code), {jsoned_entry: target.id})
    redis.zadd('operation', {jsoned_entry: target.id})
