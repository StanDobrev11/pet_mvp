import threading


_thread_locals = threading.local()


def get_current_request():
    """
    Used to access request through the project
    """

    return getattr(_thread_locals, 'request', None)


class RequestMiddleware:
    """
    Used to access request through the project using get_current_request
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response
