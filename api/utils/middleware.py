import uuid



class LoggingMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Add Request ID
        environ['X_REQUEST_ID'] = str(uuid.uuid4())
        return self.app(environ, start_response)