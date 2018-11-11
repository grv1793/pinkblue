try:
    from django.utils.deprecation import MiddlewareMixin as _MiddlewareMixin
except ImportError:
    _MiddlewareMixin = object


class MiddlewareMixin(_MiddlewareMixin):
    def __init__(self, get_response):
        """We allow next_layer to be None because old-style middlewares
        won't accept any argument.
        """
        self.get_response = get_response

    def process_request(self, request):
        """Let's handle old-style request processing here, as usual."""
        pass

    def process_response(self, request, response):
        """Let's handle old-style response processing here, as usual."""
        # Do something with response, possibly using request.
        return response

    def __call__(self, request):
        """Handle new-style middleware here."""
        response = self.process_request(request)
        if response is None:
            # If process_request returned None, we must call the next middleware or
            # the view. Note that here, we are sure that self.get_response is not
            # None because this method is executed only in new-style middlewares.
            response = self.get_response(request)

        response = self.process_response(request, response)
        return response
