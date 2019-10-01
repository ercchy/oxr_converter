from http import HTTPStatus

from decimal import Decimal
from flask import Blueprint, request, jsonify

from ..cache.redis import redis
from ..models.database import db
from ..models.convert_data import ConvertData, converted_data_schema
from ..utils.processors import get_oxr_price, validate_data, ConversionError, validate_code_value, ValidationError

from ..constants import OXR_REQUEST_URL, PRECISION

bp = Blueprint('api_v1', __name__)

import logging
logger = logging.getLogger('werkzeug')


@bp.route("/grab_and_save", methods=['POST'])
def grab_and_save():
    request_body = request.get_json()
    request_id = request.environ['X_REQUEST_ID']
    code = request_body.get('code', None)
    amount = request_body.get('amount', None)

    try:
        # Validate and clean the input data
        code, requested_amount = validate_data(code, amount)

        # Retrieve the price of the requested currency in USD
        oxr_price = get_oxr_price(url=OXR_REQUEST_URL, code=code)

        # Multiply the converted amount
        calculated_amount = Decimal(requested_amount/oxr_price).quantize(PRECISION, rounding='ROUND_UP')

    except ValidationError as err:
        return jsonify(sucess=False,
                       message="Validation failed. {}".format(err),
                       status=HTTPStatus.BAD_REQUEST.value,
                       detail=HTTPStatus.BAD_REQUEST.description
                       ), HTTPStatus.BAD_REQUEST
    except ConversionError as err:
        return jsonify(sucess=False,
                       message="Conversion failed. {}".format(err),
                       status=HTTPStatus.GATEWAY_TIMEOUT.value,
                       detail=HTTPStatus.GATEWAY_TIMEOUT.description
                       ), HTTPStatus.GATEWAY_TIMEOUT
    except Exception as err:
        return jsonify(sucess=False,
                       message="Server error. {}".format(err),
                       status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                       detail=HTTPStatus.INTERNAL_SERVER_ERROR.description
                       ), HTTPStatus.INTERNAL_SERVER_ERROR

    data = {
        'currency_code': code,
        'requested_amount': requested_amount,
        'oxr_price': oxr_price,
        'final_amount': calculated_amount,
        'request_id': request_id,
    }

    converted_data = ConvertData(**data)

    # TODO: Make this code asynchronous with usage of queue
    db.session.add(converted_data)
    try:
        db.session.commit()
    except Exception as err:
        logger.error('The object couldnt be added to the DB. {}'.format(err))
        return jsonify(sucess=False,
                       message=str(err),
                       status=HTTPStatus.INTERNAL_SERVER_ERROR.value,
                       detail=HTTPStatus.INTERNAL_SERVER_ERROR.description
                       ), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        return converted_data_schema.jsonify(data), HTTPStatus.CREATED



def get_data(limit, operations, query_filter, redis_key):
    # Get from Redis
    redis_raw_data = redis.zrange(redis_key, 0, limit - 1, desc=True)
    operations['data_from_redis'] = [eval(entry) for entry in redis_raw_data]
    # Get from MySql
    db_query = ConvertData.query.order_by(ConvertData.id.desc())
    filtered_data = db_query.filter_by(**query_filter).limit(limit).all()
    operations['data_from_mysql'] = [entry.to_dict for entry in filtered_data]


@bp.route("/last", methods=['GET'])
def get_last_record():

    args = request.args

    currency = args.get('currency', None)
    records = args.get('records', None)

    operations = {}
    operations['params'] = dict(currency=False, operations=False)
    redis_key = 'operation'
    limit = 1
    query_filter = {}

    # TODO: optimize all

    # TODO: Fix edge case when user sends empty value
    if not currency and not records :

        get_data(limit, operations, query_filter, redis_key)

        return jsonify(operations)

    if currency is not None and currency != '':
        try:
            currency = validate_code_value(currency)

        except Exception as err:
            return jsonify(sucess=False,
                           message='{}'.format(err),
                           status=HTTPStatus.BAD_REQUEST.value,
                           detail=HTTPStatus.BAD_REQUEST.description
                           ), HTTPStatus.BAD_REQUEST
        finally:
            operations['params']['currency'] = True
            redis_key = currency
            query_filter = {'currency_code': currency}

    if records is not None and records != '':
        try:
            records = int(records)
            assert records > 0, "Records needs to be an positive number"
        except Exception as err:
            return jsonify(sucess=False,
                           message='{}'.format(err),
                           status=HTTPStatus.BAD_REQUEST.value,
                           detail=HTTPStatus.BAD_REQUEST.description
                           ), HTTPStatus.BAD_REQUEST
        finally:
            operations['params']['operations'] = True
            limit = records

    get_data(limit, operations, query_filter, redis_key)

    return jsonify(operations)



