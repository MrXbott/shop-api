from fastapi import status

class SessionException(Exception):
    def __init__(self, message: str, status_code: status):
        self.message = message or self.__class__.__name__
        self.status_code = status_code
        super().__init__(message)

class SessionNotFound(SessionException):
    def __init__(self, message='Session not found'):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class SessionIdNotFound(SessionException):
    def __init__(self, message='Session ID missing in token payload'):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)