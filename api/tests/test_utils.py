import pytest
import requests
from decimal import Decimal

from ..utils.processors import validate_code_value, validate_amount, get_oxr_price


def test_validate_code():
    # asert
    assert validate_code_value('EUR')

    with pytest.raises(Exception):
        assert validate_code_value('GGGGGGGGG')

    with pytest.raises(Exception):
        assert validate_code_value('')

    with pytest.raises(Exception):
        assert validate_code_value('442.2')


def test_validate_data_function():
    # asert
    assert validate_amount(23.556)

    assert validate_amount('442.2')

    assert True == isinstance(validate_amount('4556.33'), Decimal)

    with pytest.raises(Exception):
        assert validate_amount('')

    with pytest.raises(Exception):
        assert validate_amount('   ')

    with pytest.raises(Exception):
        assert validate_amount(0000000000000)

def test_get_oxr_price_function(requests_mock):
    # TODO: Mock request and test
    requests_mock.get('http://test.com', text='data')
    # assert 'data' == requests.get('http://test.com').text
    with pytest.raises(Exception):
        assert get_oxr_price(url=None, code=None)
    # assert 'data' == get_oxr_price(url=None, code=None)

    with pytest.raises(Exception):
        assert get_oxr_price(url=None, code='EUR')

    with pytest.raises(Exception):
        assert get_oxr_price(url='http://test.com', code='EUR')