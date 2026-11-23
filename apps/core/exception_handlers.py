from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    PermissionDenied,
)

from .exceptions import ApplicationError


def custom_exception_handler(exc, context):

    # -------------------------------------------------
    # 1. Business errors
    # -------------------------------------------------
    if isinstance(exc, ApplicationError):
        return Response(
            {
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=exc.status_code,
        )

    # -------------------------------------------------
    # 2. DRF errors
    # -------------------------------------------------
    response = exception_handler(exc, context)

    if response is not None:

        code = "error"
        message = "An error occurred."
        details = response.data

        if isinstance(exc, ValidationError):
            code = "validation_error"
            message = "Please correct the errors below."
            details = response.data

        elif isinstance(exc, NotAuthenticated):
            code = "not_authenticated"
            message = "Authentication credentials were not provided."
            details = None

        elif isinstance(exc, PermissionDenied):
            code = "permission_denied"
            message = "You do not have permission to perform this action."
            details = None

        return Response(
            {
                "error": {
                    "code": code,
                    "message": message,
                    "details": details,
                }
            },
            status=response.status_code,
        )

    # -------------------------------------------------
    # 3. System errors
    # -------------------------------------------------
    return Response(
        {
            "error": {
                "code": "server_error",
                "message": "Internal server error",
                "details": {type(exc).__name__: str(exc)},
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
