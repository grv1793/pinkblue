from threading import current_thread
from assignment.middleware_mixin import MiddlewareMixin
from rest_framework.authentication import SessionAuthentication

_requests = {}
user = None


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def current_request():
    return _requests.get(current_thread().ident)


class RequestMiddleware(MiddlewareMixin):

    def process_request(self, request):
        _requests[current_thread().ident] = request

    def process_response(self, request, response):
        # when response is ready, request should be flushed
        _requests.pop(current_thread().ident, None)
        return response

    def process_exception(self, request, exception):
        # if an exception has happened, request should be flushed too
        _requests.pop(current_thread().ident, None)
        raise exception
