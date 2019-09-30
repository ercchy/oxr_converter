import json
from decimal import Decimal, InvalidOperation

from ..cache.redis import redis
from ..utils.request_utils import requests_retry_session

from ..constants import PRECISION, CURRENCY_CATALOG

import logging
logger = logging.getLogger('werkzeug')

class ValidationError(Exception):
    pass

class ConversionError(Exception):
    pass


def validate_code_value(code):
    if code:
        code = code.upper()
        try:
            codes = redis.get('codes').decode().split(',')
        except:
            codes = CURRENCY_CATALOG

        if not code in codes:
            logger.error('Request came in with an invalid code request ({}).'.format(code))
            raise ValidationError('{} is not a valid code format'.format(code))
        return code
    raise ValidationError('No currency code given')


# TODO: Write tests for this
def validate_data(code, amount):

    currency_code = validate_code_value(code)

    if amount is None:
        logger.error('Request came in with an empty value for the amount.')
        raise ValidationError('Amount can not be empty.')
    try:
        # Cast the value to the Decimal type
        requested_amount = Decimal(amount).quantize(PRECISION)
    except InvalidOperation as err:
        logger.error('Request came in with the wrong type for the amount.')
        raise ValidationError('Amount is not sent in the right format.')

    return currency_code, requested_amount


# TODO: Write tests for this
def get_oxr_price(url=None, code=None):
    response = {}

    # Set the guard against the empty URL for request
    if not url:
        logging.error('The OXR url is not set')
        raise ConversionError('URL for the OXR is not set')

    # TODO: Make a cron job (or lambda) to retrieve values in redis and read from there

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
            rates_keys = rates.keys()
            redis.set('codes', ','.join(rates_keys))

            if code in rates.keys():
                return Decimal(rates[code]).quantize(PRECISION, rounding='ROUND_UP')
            logging.error('The currency code is not correct.')
            raise ConversionError('The currency code is not available.')

        logging.error('Request to OXR was successful, but we did not get back any content')
        raise ConversionError('Request got no response')