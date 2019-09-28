import simplejson as json
from http import HTTPStatus

from decimal import Decimal
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from ..cache.redis import redis
from ..models.database import db
from ..models.convert_data import ConvertData, convert_data_schema
from ..utils.processors import get_oxr_price, validate_data, ConversionError, ValidationError

from ..constants import OXR_REQUEST_URL, PRECISION

bp = Blueprint('api_v1', __name__)

import logging
logger = logging.getLogger('werkzeug')


@bp.route("/grab_and_save", methods=['POST'])
def grab_and_save():
    request_body = request.get_json()
    request_id = request.environ['X_REQUEST_ID']

    try:
        # Validate and clean the input data
        code, requested_amount = validate_data(request_body)
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
    db.session.add(converted_data)

    # TODO: Error handle
    redis.set('{}:{}:{}'.format(code, request_id, 0), 0)
    redis.hset(request_id, 'operation', json.dumps(data, use_decimal=True))

    try:
        db.session.commit()
    except IntegrityError as err:
        logger.error('The object couldnt be added to the DB. {}'.format(err))
        return jsonify(sucess=False,
                       message=str(err.orig),
                       status=HTTPStatus.BAD_REQUEST.value,
                       detatil=HTTPStatus.BAD_REQUEST.description,
                       ), HTTPStatus.BAD_REQUEST
    finally:
        return convert_data_schema.jsonify(converted_data), HTTPStatus.CREATED


@bp.route("/last", methods=['GET'])
def get_last_record():
    #TODO: validate code
    #code = validate_data(code)
    args = request.args
    code = args.get('code', None)
    records = args.get('records', None)

    if code and records:
        ret_val = db.session.query(ConvertData).order_by('id desc').limit(records)
    elif code:
        ret_val = db.session.query(ConvertData).filter_by(currency_code=code).limit(1)
    elif records:
        ret_val = ConvertData.queryn.filter_by(currency_code=code).limit(records)
    else:
        ret_val = db.session.query(ConvertData).first()
    import ipdb;ipdb.set_trace()

    return convert_data_schema.jsonify(ret_val)