from flask import json
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


def validate_amount(amount):
    """
    Casts the passed argument into Decimal number

    It does not make a percision of 8 digits yet,
    as that could make us loose money

    :param amount: Decimal
    :return: Decimal
    """
    if amount:
        try:
            # Cast the value to the Decimal type
            requested_amount = Decimal(amount)
        except InvalidOperation as err:
            logger.error('Request came in with the wrong type for the amount.')
            raise ValidationError('Amount is not sent in the right format.')

        return requested_amount

    logger.error('Request came in with an empty value for the amount.')
    raise ValidationError('Amount can not be empty.')


def validate_data(code, amount):
    """
    Runs the validation functions on code and amount
    """
    return validate_code_value(code), validate_amount(amount)


def set_oxr_rates_to_cache(rates_keys):
    # TODO: Update this list only once an hour, no need to update it every time
    # Updating the list of codes to the redis
    try:
        redis.set('codes', ','.join(rates_keys))
    except Exception as err:
        logging.warning('The codes were not written to the redis database. {}'.format(err))

    return rates_keys


# TODO: Write tests for this
def get_oxr_price(url=None, code=None):
    response = {}

    # Set the guard against the empty URL for request
    if not url:
        logging.error('The OXR url is not set')
        raise ConversionError('URL for the OXR is not set')

    # TODO: Make a cron job (or lambda) to retrieve values in redis and read from there

    # Retrieve data from the OXR
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

            set_oxr_rates_to_cache(rates_keys)

            if code in rates_keys:
                return Decimal(rates[code]).quantize(PRECISION, rounding='ROUND_UP')

            logging.error('The currency code is not correct.')
            raise ConversionError('The currency code is not available.')

        logging.error('Request to OXR was successful, but we did not get back any content')
        raise ConversionError('Request got no response')
