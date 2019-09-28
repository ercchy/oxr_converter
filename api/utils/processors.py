import json
from decimal import Decimal, InvalidOperation

from ..cache import redis
from ..utils.request_utils import requests_retry_session

from ..constants import PRECISION

import logging
logger = logging.getLogger('werkzeug')

class ValidationError(Exception):
    pass

class ConversionError(Exception):
    pass


# TODO: Write tests for this
def validate_data(request_body):
    # Check if
    # 1. values are set
    # 2. are the right type
    currency_code = request_body.get('code', None)
    requested_amount = request_body.get('amount', None)

    # set guard for None values
    if currency_code is None:
        logger.error('Request came in with an empty value for the code.')
        raise ValidationError('Code can not be empty.')

    if requested_amount is None:
        logger.error('Request came in with an empty value for the amount.')
        raise ValidationError('Amount can not be empty.')

    try:
        # Cast the value to the Decimal type
        requested_amount = Decimal(requested_amount).quantize(PRECISION)
    except InvalidOperation:
        logger.error('Request came in with the wrong type for the amount.')
        raise ValidationError('Amount is not sent in the right format.')
    return currency_code.upper(), requested_amount


# TODO: Write tests for this
def get_oxr_price(url=None, code=None):
    response = {}

    # Set the guard against the empty URL for request
    if not url:
        logging.error('The OXR url is not set')
        raise ConversionError('URL for the OXR is not set')

    # TODO: Set the catalog into Redis, to read from it???

    try:
        response = requests_retry_session().get(url)
    except Exception as x:
        logger.error('Request to the OXR failed: '.format(x.__class__.__name__))
        raise ConversionError()
    else:
        logger.info('Request to the OXR was successful.')
    finally:
        if response.content:
            content_dict = json.loads(response.content)
            rates = content_dict.get('rates', None)
            import ipdb;ipdb.set_trace()
            redis.set('codes', rates.keys())

            if code in rates.keys():
                return Decimal(rates[code]).quantize(PRECISION, rounding='ROUND_UP')
            logging.error('The currency code is not correct.')
            raise ConversionError('The currency code is not available.')

        logging.error('Request to OXR was successful, but we did not get back any content')
        raise ConversionError('Request got no response')