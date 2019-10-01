import uuid

class LoggingMiddleware(object):
    """
    We will add a request ID to the request object.

    It will enable us to return the information about the objects,
    without having to dispose the ID.

    It also helps with the searching trough logs, shall anything goes wrong.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Add Request ID
        environ['X_REQUEST_ID'] = str(uuid.uuid4())
        return self.app(environ, start_response)