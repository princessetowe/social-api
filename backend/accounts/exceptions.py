
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import Throttled
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled) and hasattr(exc, 'wait'):

        detail = {
            'error': 'Too many requests',
            'message': f'Please try again in {exc.wait} seconds.'
        }

        return Response(detail, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    return response
