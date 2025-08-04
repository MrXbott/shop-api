from fastapi import status

class TokenException(Exception):
    def __init__(self, message: str = None, status_code: status = status.HTTP_400_BAD_REQUEST):
        self.message = message or self.__class__.__name__
        self.status_code = status_code
        super().__init__(message)
        self.message = message

class TokenNotFound(TokenException):
    def __init__(self, message='Token not found'):
        super().__init__(message, status.HTTP_404_NOT_FOUND)