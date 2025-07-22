class UserException(Exception):
    pass

class InvalidUserIdFormat(UserException):
    pass

class UserNotFound(UserException):
    pass

class CreateUserException(UserException):
    pass

class UpdateUserException(UserException):
    pass