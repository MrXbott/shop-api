from fastapi import status

class UserException(Exception):
    def __init__(self, message: str = None, status_code: status = status.HTTP_400_BAD_REQUEST):
        self.message = message or self.__class__.__name__
        self.status_code = status_code
        super().__init__(message)
        self.message = message

class InvalidUserIdFormat(UserException):
    def __init__(self, message: str = 'Invalid user ID format'):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

class UserNotFound(UserException):
    def __init__(self, message='User not found'):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class CreateUserException(UserException):
    def __init__(self, message: str = 'Failed to create user'):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserEmailAlreadyExists(UserException):
    def __init__(self, message: str = 'User with this email already exists'):
        super().__init__(message, status.HTTP_409_CONFLICT)

class UpdateUserException(UserException):
    def __init__(self, message: str = 'Failed to update user'):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)