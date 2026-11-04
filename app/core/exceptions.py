
class ApplicationException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationException(ApplicationException):
    def __init__(self, message: str = "Authentication required: Security context was not provided."):
        super().__init__(message, status_code=401)


class UnauthorizedException(ApplicationException):
    def __init__(self, message: str = "Unauthorized: Operation not permitted for this actor or role."):
        super().__init__(message, status_code=403)


class ExternalAPIException(ApplicationException):
    def __init__(self, message: str):
        super().__init__(message, status_code=502)


class ResourceNotFoundException(ApplicationException):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class ValidationException(ApplicationException):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
