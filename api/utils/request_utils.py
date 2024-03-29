import logging
import requests
from flask import has_request_context, request
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..constants import RETRIES


# Reference: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
# Documentatin for Retry class: https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.retry
def requests_retry_session(retries=RETRIES, backoff_factor=0.3,
                           status_forcelist=(500, 502, 504),
                           session=None):
    """
    The method will try hitting the requested url for how much retries we
    define in the constants file.
    Between the retries it will wait for `backoff_factor`, which will exponentially grow
    with the number of retries.

    :param retries: Defined in the constants
    :param backoff_factor: A backoff factor to apply between attempts after the second try
    :param status_forcelist: A set of integer HTTP status codes that we should force a retry on
    :param session: You can pass an alredy alive session
    :return: session
    """

    if not session:
        session = requests.Session()

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)