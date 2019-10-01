import os
import tempfile

import pytest

from api import run


@pytest.fixture
def client():
    db_fd, run.application.config['DATABASE'] = tempfile.mkstemp()
    run.application.config['TESTING'] = True

    with run.application.test_client() as client:
        with run.application.app_context():
            run.db()
        yield client

    os.close(db_fd)
    os.unlink(run.application.config['DATABASE'])

def test_index(client):
    # rv = client.get('/')
    # assert b'No entries here so far' in rv.data
    pass