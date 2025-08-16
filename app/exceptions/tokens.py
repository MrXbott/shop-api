from fastapi import status

class TokenException(Exception):
    def __init__(self, message: str, status_code: status):
        self.message = message or self.__class__.__name__
        self.status_code = status_code
        super().__init__(message)

class TokenNotFound(TokenException):
    def __init__(self, message='Token not found'):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class InvalidToken(TokenException):
    def __init__(self, message='Invalid token'):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class InvalidTokenPayload(TokenException):
    def __init__(self, message='Invalid token payload'):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class ExpiredToken(TokenException):
    def __init__(self, message='Token has expired'):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)