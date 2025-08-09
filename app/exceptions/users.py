from fastapi import status

class UserException(Exception):
    def __init__(self, message: str, status_code: status):
        self.message = message or self.__class__.__name__
        self.status_code = status_code
        super().__init__(message)

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

class UserNoUpdateData(UserException):
    def __init__(self, message: str = 'No data to update the user. At least one field must be provided for update.'):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)