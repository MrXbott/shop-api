from fastapi import status

class RoleException(Exception):
    def __init__(self, message: str, status_code: status):
        self.message = message or self.__class__.__name__
        self.status_code = status_code
        super().__init__(message)

class RoleNotFound(RoleException):
    def __init__(self, message='Role not found'):
        super().__init__(message, status.HTTP_404_NOT_FOUND)