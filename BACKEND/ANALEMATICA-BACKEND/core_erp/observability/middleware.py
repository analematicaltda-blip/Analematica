import uuid
import contextvars

_correlation_id = contextvars.ContextVar('correlation_id', default=None)

def get_correlation_id():
    return _correlation_id.get() or str(uuid.uuid4())

def set_correlation_id(cid):
    return _correlation_id.set(cid)

class CorrelationIDMiddleware:
    """
    Middleware to start and propagate a correlation_id for every request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        correlation_id = request.headers.get('X-Correlation-ID') or str(uuid.uuid4())

        token = set_correlation_id(correlation_id)
        request.correlation_id = correlation_id

        response = self.get_response(request)
        response['X-Correlation-ID'] = correlation_id

        _correlation_id.reset(token)
        return response
