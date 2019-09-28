from http import HTTPStatus

from decimal import Decimal
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

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

    # TODO: save to Redis and to DB
    # TODO: set the strategy
    converted_data = ConvertData(
        currency_code=code,
        requested_amount=requested_amount,
        oxr_price = oxr_price,
        final_amount = calculated_amount
    )
    db.session.add(converted_data)

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
    return jsonify({'msg': 'Heave all the data'})